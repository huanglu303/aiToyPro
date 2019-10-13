import os

from flask import jsonify
from flask import send_file
from flask import Blueprint

from config import DB
from config import COVER_PATH
from config import MUSIC_PATH

content_blue = Blueprint("content_blue", __name__)


# 获取内容信息
@content_blue.route("/content_list", methods=["POST"])
def content_list():
    content = list(DB.Source.find({}))

    for item in content:
        item["_id"] = str(item["_id"])

    return jsonify(content)


# 获取封面
@content_blue.route("/get_cover/<filename>")
def get_cover(filename):
    cover_path = os.path.join(COVER_PATH, filename)

    return send_file(cover_path)


# 获取资源
@content_blue.route("/get_music/<filename>")
def get_music(filename):
    music_path = os.path.join(MUSIC_PATH, filename)

    return send_file(music_path)
