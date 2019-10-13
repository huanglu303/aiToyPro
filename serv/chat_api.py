import os
from uuid import uuid4

from bson import ObjectId
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import send_file

from config import DB
from config import RET
from config import RECOFILE_PATH
from utils.cache import get_redis
from utils.cache import get_redis_toy
from utils.media_utils import t2s

chat_blue = Blueprint("chat_blue", __name__)


# 获取聊天记录列表
@chat_blue.route("/chat_list", methods=["POST"])
def chat_list():
    chat_data = request.form.to_dict()  # {chat_id: chat_id, from_user: from_user, to_user: to_user}
    # print(chat_data)
    chat_id = ObjectId(chat_data["chat_id"])

    chats_list = DB.Chats.find_one({"_id": chat_id})["chat_list"]

    get_redis(chat_data["to_user"], chat_data["from_user"])

    RET["CODE"] = 0
    RET["MSG"] = "查询聊天记录"
    RET["DATA"] = chats_list

    return jsonify(RET)


# 收取语音消息
@chat_blue.route("/recv_msg", methods=["POST"])
def recv_msg():
    recv_msg_list = []

    user_data = request.form.to_dict()  # {from_user: user_id/toy_id, to_user: toy_id, from_user_type: toy/app}
    # print(user_data)
    friend_type = user_data.pop("from_user_type")
    # print(user_list)
    filename = f"{uuid4()}.wav"  # 生成唯一文件名
    path = os.path.join(RECOFILE_PATH, filename)  # 拼接文件保存路径

    count, from_user = get_redis_toy(user_data["to_user"], user_data["from_user"])  # 获取未读消息相关信息
    # print(count, from_user)
    user_data["from_user"] = from_user  # 更新发送方信息
    user_list = list(user_data.values())  # [user_id/toy_id, toy_id]

    if not count:  # 若未读消息为 0
        t2s(text="现在没有任何消息", path=path)  # 合成语音消息提醒
        # 构建返回信息
        recv = {
            "from_user": user_data["from_user"],
            "chat": filename,
        }

        # 将返回信息追加到消息列表当中
        recv_msg_list.append(recv)

    else:  # 若未读消息不为 0
        # 获取接收方 (toy) 的通讯录
        friend_list = DB.Toys.find_one({"_id": ObjectId(user_data["to_user"])})["friend_list"]
        # 遍历接收方的通讯录, 通过发送方 ID 进行定位, 获取发送方 remark (friend_remark) 及 type (friend_type)
        for chat_info in friend_list:
            if chat_info["friend_id"] == user_data["from_user"]:
                friend_remark = chat_info["friend_remark"]
                friend_type = chat_info["friend_type"]
                t2s(text=f"以下是来自{friend_remark}的{count}条消息", path=path)  # 合成语音消息提醒

        # 构建返回信息
        recv = {
            "from_user": user_data["from_user"],
            "chat": filename,
        }

        # print(user_list)
        # 根据未读消息数量 (count) 获取属于收发双方的所有未读消息
        chats_list = DB.Chats.find_one({"user_list": {"$all": user_list}})["chat_list"][-count:]  # 子集查询
        # print(chats_list)
        recv_msg_list.extend(chats_list)  # 将查询结果迭代追加到消息列表当中
        recv_msg_list.reverse()  # 反转列表 (调整消息读取顺序)
        recv_msg_list.append(recv)  # 将消息提醒追加到消息列表当中 (通过前端代码了解到消息数据通过 pop 取得)

    # 构建返回值数据结构
    ret = {
        "from_user": from_user,
        "friend_type": friend_type,
        "chat_list": recv_msg_list
    }

    return jsonify(ret)


# 播放语音消息
@chat_blue.route("/get_chat/<chat_name>")  # 通过动态路由参数获取语音消息文件
def get_chat(chat_name):
    chat_name_path = os.path.join(RECOFILE_PATH, chat_name)  # 拼接语音消息文件路径
    # print(chat_name_path)
    return send_file(chat_name_path)  # 发送语音消息文件
