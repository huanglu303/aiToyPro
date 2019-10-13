import os
import subprocess
import time
from uuid import uuid4

from bson import ObjectId
from flask import Blueprint
from flask import request
from flask import jsonify

from config import DB
from config import RET
from config import RECOFILE_PATH
from utils.cache import set_redis
from utils.media_utils import t2s
from utils.media_utils import a2t
from utils.media_utils import nlp_no1

uploader_blue = Blueprint("uploader_blue", __name__)


# App 向 Toy 发送语音消息
@uploader_blue.route("/app_uploader", methods=["POST"])
def app_uploader():
    only_name = uuid4()
    data = request.form.to_dict()  # {user_id: user_id, to_user: toy_id}
    # print(data)
    user_list = list(data.values())
    file = request.files["reco_file"]

    file_name = f"{only_name}.amr"  # 生成唯一文件名

    file_path = os.path.join(RECOFILE_PATH, file_name)  # 拼接语音文件保存路径 (以唯一文件名命名)
    file.save(file_path)  # 持久化语音文件
    subprocess.getoutput(f"ffmpeg -i {file_path} {file_path}.mp3")  # 格式转换 (目的使浏览器识别)

    path = os.path.join(RECOFILE_PATH, f"{data['user_id']}.mp3")  # 拼接语音提醒文件的存放路径 (以 from_user 命名)
    # 获取接收方 (toy) 的通讯录
    friend_list = DB.Toys.find_one({"_id": ObjectId(data["to_user"])})["friend_list"]
    for chat_info in friend_list:  # 遍历接收方的通讯录, 通过发送方 ID 进行定位, 获取发送方 remark (friend_remark)
        if chat_info["friend_id"] == data["user_id"]:
            t2s(remark=chat_info["friend_remark"], path=path)  # 生成语音提醒文件

    file_name = f"{file_name}.mp3"  # 更新文件名

    # 构建语音消息格式
    chat_data = {
        "from_user": data["user_id"],
        "to_user": data["to_user"],
        "chat": file_name,
        "createTime": time.time()
    }

    # 更新 Chats 将构建好的语音消息追加到属于收发双方的 chat_list 当中
    DB.Chats.update_one({"user_list": {"$all": user_list}}, {"$push": {"chat_list": chat_data}})
    set_redis(data["to_user"], data["user_id"])  # 缓存 1 条未读消息

    RET["CODE"] = 0
    RET["MSG"] = "上传成功"
    RET["DATA"] = {
        "filename": f"{data['user_id']}.mp3",  # 返回消息提醒
        # "filename": file_name,
        "friend_type": "app"
    }

    return jsonify(RET)


# Toy 向 App 发送语音消息
@uploader_blue.route("/toy_uploader", methods=["POST"])
def toy_uploader():
    only_name = uuid4()
    data = request.form.to_dict()  # {to_user: to_user, user_id: toy_id, friend_type: app/toy}
    friend_type = data.pop("friend_type")
    user_list = list(data.values())
    file = request.files["reco"]

    file_name = f"{only_name}.wav"
    file_path = os.path.join(RECOFILE_PATH, file_name)
    file.save(file_path)

    if friend_type == "toy":  # 若消息接收方的类型为 toy
        path = os.path.join(RECOFILE_PATH, f"{data['user_id']}.mp3")  # 拼接语音提醒文件的存放路径
        # 获取接收方 (toy) 的通讯录
        friend_list = DB.Toys.find_one({"_id": ObjectId(data["to_user"])})["friend_list"]
        for chat_info in friend_list:  # 遍历接收方的通讯录, 通过发送方 ID 进行定位, 获取发送方 remark (friend_remark)
            if chat_info["friend_id"] == data["user_id"]:
                t2s(remark=chat_info["friend_remark"], path=path)

        RET["CODE"] = 0
        RET["MSG"] = "上传成功"
        RET["DATA"] = {
            "filename": f"{data['user_id']}.mp3",  # 消息提醒
            "friend_type": "toy"
        }
    else:
        RET["CODE"] = 0
        RET["MSG"] = "上传成功"
        RET["DATA"] = {
            "filename": file_name,
            "friend_type": "toy"
        }

    chat_data = {
        "from_user": data["user_id"],
        "to_user": data["to_user"],
        "chat": file_name,
        "createTime": time.time()
    }

    DB.Chats.update_one({"user_list": {"$all": user_list}}, {"$push": {"chat_list": chat_data}})
    set_redis(data["to_user"], data["user_id"])  # 缓存 1 条未读消息

    return jsonify(RET)


# Toy 向 AI 发送语音指令
@uploader_blue.route("/ai_uploader", methods=["POST"])
def ai_uploader():
    toy_data = request.form.to_dict()  # {toy_id: toy_id}
    # print(toy_data)
    file = request.files.get("reco")
    q_path = os.path.join(RECOFILE_PATH, f"{uuid4()}.wav")
    file.save(q_path)

    text = a2t(q_path)  # 将语音消息转换为文字

    res = nlp_no1(text, toy_data["toy_id"])  # 通过 NLP 进行处理

    return res
