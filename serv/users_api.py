from bson import ObjectId
from flask import Blueprint, jsonify, request

from config import DB, RET
from utils.cache import get_all_redis

user_blue = Blueprint("user_blue", __name__)


# 注册
@user_blue.route("/reg", methods=["POST"])
def reg():
    reg_data = request.form.to_dict()

    reg_data["avatar"] = "baba.jpg" if reg_data.get("gender") == "2" else "mama.jpg"
    reg_data["bind_toys"] = []
    reg_data["friend_list"] = []

    DB.Users.insert_one(reg_data)

    return jsonify({"CODE": 0, "MSG": "注册成功", "DATA": {}})


# 登录
@user_blue.route("/login", methods=["POST"])
def login():
    login_data = request.form.to_dict()
    user_info = DB.Users.find_one(login_data)

    user_info["_id"] = str(user_info.get("_id"))

    RET["CODE"] = 0
    RET["MSG"] = f"欢迎{user_info.get('nickName')}登录"
    RET["DATA"] = user_info

    return jsonify(RET)


# 自动登录
@user_blue.route("/auto_login", methods=["POST"])
def auto_login():
    user_data = request.form.to_dict()
    user_data["_id"] = ObjectId(user_data.get("_id"))

    user_info = DB.Users.find_one(user_data)
    user_info["_id"] = str(user_info.get("_id"))

    count_dict = get_all_redis(user_info["_id"])
    user_info["chat"] = count_dict

    RET["CODE"] = 0
    RET["MSG"] = f"欢迎{user_info.get('nickName')}登录"
    RET["DATA"] = user_info

    return jsonify(RET)
