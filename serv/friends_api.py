from bson import ObjectId
from flask import Blueprint, request, jsonify

from config import DB, RET

friends_blue = Blueprint("friends_blue", __name__)


# 好友列表
@friends_blue.route("/friend_list", methods=["POST"])
def friend_list():
    user_data = request.form.to_dict()  # ["_id": str(_id)]
    user_data["_id"] = ObjectId(user_data["_id"])

    friends_list = DB.Users.find_one(user_data)["friend_list"]

    RET["CODE"] = 0
    RET["MSG"] = "好友查询"
    RET["DATA"] = friends_list

    return jsonify(RET)


# 添加好友请求
@friends_blue.route("/add_req", methods=["POST"])
def add_req():
    req_data = request.form.to_dict()
    # print(req_data)
    add_type = req_data["add_type"]  # 好友请求来源的类型 toy/app
    response_data = DB.Toys.find_one({"_id": ObjectId(req_data["toy_id"])})  # 获取被请求方数据

    # 根据请求来源类型构建请求信息
    if add_type == "toy":  # 来自于 toy
        request_data = DB.Toys.find_one({"_id": ObjectId(req_data["add_user"])})
        req_data["avatar"] = request_data["avatar"]
        req_data["nickname"] = request_data["baby_name"]
        req_data["status"] = 0
        req_data["toy_name"] = response_data["toy_name"]
    else:  # 来自于 user
        request_data = DB.Users.find_one({"_id": ObjectId(req_data["add_user"])})
        req_data["avatar"] = request_data["avatar"]
        req_data["nickname"] = request_data["baby_name"]
        req_data["status"] = 0
        req_data["toy_name"] = response_data["toy_name"]

    DB.Request.insert_one(req_data)  # 请求信息持久化

    RET["CODE"] = 0
    RET["MSG"] = "添加好友请求成功"
    RET["DATA"] = {}

    return jsonify(RET)


# 好友请求列表
@friends_blue.route("/req_list", methods=["POST"])
def req_list():
    req_data = request.form.to_dict()
    # print(req_data)
    # 通过 Users 的 bind_toys 字段获取到当前 user 所有已绑定 toy
    toys_list = DB.Users.find_one({"_id": ObjectId(req_data["user_id"])})["bind_toys"]
    # 获取所有未处理好友请求信息
    request_list = list(DB.Request.find({"toy_id": {"$in": toys_list}, "status": 0}))
    for item in request_list:
        item["_id"] = str(item["_id"])

    RET["CODE"] = 0
    RET["MSG"] = "查询好友请求"
    RET["DATA"] = request_list

    return jsonify(RET)


# 同意好友请求
@friends_blue.route("/acc_req", methods=["POST"])
def acc_req():
    req_data = request.form.to_dict()
    # print(req_data)
    request_data = DB.Request.find_one({"_id": ObjectId(req_data["req_id"])})  # 获取好友请求具体信息

    chat_data = {
        "user_list": [request_data["add_user"], request_data["toy_id"]],
        "chat_list": []
    }
    chat_id = DB.Chats.insert_one(chat_data).inserted_id  # 构建 chat

    response_toy_data = DB.Toys.find_one({"_id": ObjectId(request_data["toy_id"])})
    # 响应方的信息 --向--> 请求方的 friend_list 中追加
    response2request = {
        "friend_id": request_data["toy_id"],
        "friend_nick": response_toy_data["baby_name"],
        "friend_remark": request_data["remark"],
        "friend_avatar": response_toy_data["avatar"],
        "friend_chat": str(chat_id),
        "friend_type": "toy"
    }

    # 根据请求来源类型构建请求方信息
    if request_data["add_type"] == "app":  # 来自于 app
        request_app_data = DB.Users.find_one({"_id": ObjectId(request_data["add_user"])})
        # 请求方的信息 --向--> 响应方的 friend_list 中追加
        request2response = {
            "friend_id": request_data["add_user"],
            "friend_nick": request_app_data["nickName"],
            "friend_remark": req_data["remark"],
            "friend_avatar": request_app_data["avatar"],
            "friend_chat": str(chat_id),
            "friend_type": "app"
        }

        DB.Users.update_one({"_id": ObjectId(request_data["add_user"])}, {"$push": {"friend_list": response2request}})
    else:  # 来自于 toy
        request_toy_data = DB.Toys.find_one({"_id": ObjectId(request_data["add_user"])})
        # 请求方的信息 --向--> 响应方的 friend_list 中追加
        request2response = {
            "friend_id": request_data["add_user"],
            "friend_nick": request_toy_data["baby_name"],
            "friend_remark": req_data["remark"],
            "friend_avatar": request_toy_data["avatar"],
            "friend_chat": str(chat_id),
            "friend_type": "toy"
        }

        DB.Toys.update_one({"_id": ObjectId(request_data["add_user"])}, {"$push": {"friend_list": response2request}})

    # 更新响应方好友信息
    DB.Toys.update_one({"_id": ObjectId(request_data["toy_id"])}, {"$push": {"friend_list": request2response}})
    # 跟新请求信息状态
    DB.Request.update_one({"_id": ObjectId(req_data["req_id"])}, {"$set": {"status": 1}})

    RET["CODE"] = 0
    RET["MSG"] = "同意添加好友"
    RET["DATA"] = {}

    return jsonify(RET)


# 拒绝好友请求
@friends_blue.route("/ref_req", methods=["POST"])
def ref_req():
    req_data = request.form.to_dict()

    # 更新请求信息状态
    DB.Request.update_one({"_id": ObjectId(req_data["req_id"])}, {"$set": {"status": 2}})

    RET["CODE"] = 0
    RET["MSG"] = "拒绝添加好友"
    RET["DATA"] = {}

    return jsonify(RET)
