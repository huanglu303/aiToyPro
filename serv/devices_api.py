import os

from bson import ObjectId
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import send_file

from config import DB
from config import RET
from config import QRCODE_PATH

device_blue = Blueprint("device_blue", __name__)


# 扫描二维码
@device_blue.route("/scan_qr", methods=["POST"])
def scan_qr():
    device_data = request.form.to_dict()  # {device_key: device_key}
    toy_info = DB.Toys.find_one(device_data)

    if not toy_info:  # 若 Toys 中不存在该 device_key
        device_info = DB.Devices.find_one(device_data)
        if device_info:  # 若 Devices 中存在该 device_key
            device_info["_id"] = str(device_info.get("_id"))
            RET["CODE"] = 0
            RET["MSG"] = "二维码扫描成功"
            RET["DATA"] = device_info
        else:  # 若 Devices 中不存在该 device_key
            RET["CODE"] = 1
            RET["MSG"] = "请扫描玩具二维码"
            RET["DATA"] = {}
    else:  # 若 Toys 中存在该 device_key
        toy_id = str(toy_info.get("_id"))
        RET["CODE"] = 2
        RET["MSG"] = "设备已经进行绑定"
        RET["DATA"] = {"toy_id": toy_id}

    return jsonify(RET)


# 绑定玩具
@device_blue.route("/bind_toy", methods=["POST"])
def bind_toy():
    # {toy_name: toy_name, baby_name: baby_name, remark: remark, user_id: user_id, device_key: device_key}
    toy_data = request.form.to_dict()
    # print(toy_data)
    toy_data["avatar"] = "toy.jpg"
    toy_data["friend_list"] = []

    chat_data = {
        "user_list": [],
        "chat_list": []
    }
    chat_id = DB.Chats.insert_one(chat_data).inserted_id  # 构建 chat 获取 chat_id
    toy_id = DB.Toys.insert_one(toy_data).inserted_id  # 构建 toy 获取 toy_id
    user_id = ObjectId(toy_data["user_id"])

    user_info = DB.Users.find_one({"_id": user_id})  # 获取用户信息

    # app --向--> toy 的 friend_list 中追加
    app2toy = {
        "friend_id": toy_data["user_id"],
        "friend_nick": user_info["nickName"],
        "friend_remark": "妈妈" if user_info["gender"] == "1" else "爸爸",
        "friend_avatar": user_info["avatar"],
        "friend_chat": str(chat_id),  # 创建一个 Chats 数据表 插入一条数据 inserted_id ObjectId
        "friend_type": "app"
    }

    # toy --向--> app 的 friend_list 中追加
    toy2app = {
        "friend_id": str(toy_id),
        "friend_nick": toy_data["baby_name"],
        "friend_remark": toy_data["toy_name"],
        "friend_avatar": toy_data["avatar"],
        "friend_chat": str(chat_id),
        "friend_type": "toy"
    }

    toy_data["friend_list"].append(app2toy)
    user_info["bind_toys"].append(str(toy_id))
    user_info["friend_list"].append(toy2app)
    chat_data["user_list"] = [str(toy_id), str(user_id)]

    DB.Users.update_one({"_id": user_id}, {"$set": user_info})
    DB.Toys.update_one({"_id": toy_id}, {"$set": toy_data})
    DB.Chats.update_one({"_id": chat_id}, {"$set": chat_data})

    RET["CODE"] = 0
    RET["MSG"] = "绑定完成"

    return jsonify(RET)


# 玩具列表
@device_blue.route("/toy_list", methods=["POST"])
def toy_list():
    user_data = request.form.to_dict()  # {"_id": user_id}

    # 方案 一 (繁琐, 弃用)
    # 通过 user_id 获取 Users 表中的 bind_toys 数据
    # 再通过 bind_toys 中的数据获取到 Tots 表中的数据

    # toys_list = []
    #
    # user_data["_id"] = ObjectId(user_data["_id"])
    # user_info = DB.Users.find_one(user_data)
    #
    # for toy_id in user_info["bind_toys"]:
    #     toy_info = DB.Toys.find_one({"_id": ObjectId(toy_id)})
    #     toy_info["_id"] = str(toy_info["_id"])
    #     toys_list.append(toy_info)

    # 方案 二 (简单快捷)
    # 通过 user_id 获取 Toys 表中的数据

    toys_list = list(DB.Toys.find({"user_id": user_data.get("_id")}))
    for toy_info in toys_list:
        toy_info["_id"] = str(toy_info["_id"])

    RET["CODE"] = 0
    RET["MSG"] = "获取Toy列表"
    RET["DATA"] = toys_list

    return jsonify(RET)


# 获取二维码
@device_blue.route("/get_qr/<filename>")
def get_qr(filename):
    file_path = os.path.join(QRCODE_PATH, filename)

    return send_file(file_path)


# 开启玩具
@device_blue.route("/open_toy", methods=["POST"])
def open_toy():
    device_key = request.form.to_dict()  # {device_key: device_key}
    toy_info = DB.Toys.find_one(device_key)

    if toy_info:  # 若 Toys 中存在
        ret = {
            "code": 0,
            "music": "Success.mp3",
            "toy_id": str(toy_info["_id"]),
            "name": toy_info["toy_name"]
        }
    elif DB.Devices.find_one(device_key):  # 若 Devices 中存在
        ret = {
            "code": 1,
            "music": "Nobind.mp3",
        }
    else:  # 若 Devices 中不存在
        ret = {
            "code": 2,
            "music": "Nolic.mp3",
        }

    return jsonify(ret)
