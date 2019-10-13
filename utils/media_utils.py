import os
import requests
from uuid import uuid4
import subprocess

from bson import ObjectId
from pypinyin import lazy_pinyin, TONE2

from config import RECOFILE_PATH, DB


# 文字转语音
from utils.gen_nlp import my_nlp_content


def t2s(remark=None, path=None, text=None):
    from aip import AipSpeech

    APP_ID, API_KEY, SECRET_KEY = ('APP_ID', 'API_KEY', 'SECRET_KEY')
    t2s_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    if remark:
        result = t2s_client.synthesis(f'你有来自{remark}的消息', 'zh', 1, {
            'vol': 5,
        })
    elif text:
        result = t2s_client.synthesis(text, 'zh', 1, {
            'vol': 5,
        })

    if not isinstance(result, dict):
        with open(path, 'wb') as f:
            f.write(result)


# 语音转文字
def a2t(file_path):
    from aip import AipSpeech

    APP_ID, API_KEY, SECRET_KEY = ('APP_ID', 'API_KEY', 'SECRET_KEY')
    s2t_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    def get_content(file_p):
        cmd_str = f"ffmpeg -y -i {file_p} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {file_p}.pcm"
        subprocess.getoutput(cmd_str)
        with open(f"{file_p}.pcm", 'rb') as fp:
            return fp.read()

    res = s2t_client.asr(get_content(file_path), 'pcm', 16000, {
        'dev_pid': 1536,
    })

    return res.get("result")[0]


def get_data(content):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": content
            },
        },
        "userInfo": {
            "apiKey": "apiKey",
            "userId": "001"
        }
    }

    res = requests.post("http://openapi.tuling123.com/openapi/api/v2", json=data)
    res_dict = res.json()
    return res_dict.get("results")[0].get("values").get("text")


# 自然语言处理
def nlp_no1(text, toy_id):
    filename = f"{uuid4()}.mp3"
    path = os.path.join(RECOFILE_PATH, filename)

    # text = 我要听 / 我想听 / 请播放 + "歌名" = 我要听虫儿飞
    if "我要听" in text or "我想听" in text or "请播放" in text:
        content = my_nlp_content(text)
        if content:
            return {"from_user": "ai", "music": content.get("track_name")}

    # text = 我要给 XXX 发消息
    if "发消息" in text or "聊天" in text:
        text_py = "".join(lazy_pinyin(text, style=TONE2))
        toy_info = DB.Toys.find_one({"_id": ObjectId(toy_id)})
        for friend in toy_info.get("friend_list"):
            remark_name_py = "".join(lazy_pinyin(friend["friend_remark"], style=TONE2))
            nick_name_py = "".join(lazy_pinyin(friend["friend_nick"], style=TONE2))
            if remark_name_py in text_py or nick_name_py in text_py:
                t2s(text=f"现在可以给{friend.get('friend_remark')}发消息了", path=path)
                return {
                    "from_user": friend.get("friend_id"),
                    "chat": filename,
                    "friend_type": friend.get("friend_type")
                }

    # 这里打算对接图灵机器人
    try:
        text = get_data(text)
        t2s(text=text, path=path)
    except:
        t2s("我没听清楚, 请再说一次")

    return {"from_user": "ai", "chat": filename, "friend_type": "ai"}
