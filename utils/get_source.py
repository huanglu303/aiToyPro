import os
import time
from uuid import uuid4

import execjs
import requests

from config import DB
from config import URL
from config import MUSIC_PATH
from config import COVER_PATH


# 爬取喜马拉雅服务器系统时间戳, 用于生成 xm-sign
def get_time(headers):
    url = "https://www.ximalaya.com/revision/time"
    response = requests.get(url, headers=headers)
    html = response.text

    return html


# 生成xm-sign
def exec_js(headers):
    # 获取喜马拉雅系统时间戳
    times = get_time(headers)

    # 读取同一路径下的js文件
    with open('./xmSign.js', encoding='utf-8') as f:
        js = f.read()

    # 通过compile命令转成一个js对象
    doc2js = execjs.compile(js)
    # 调用js的function
    res = doc2js.call('python', times)

    return res


# 获取资源信息及资源链接
def get_link(url):
    import json

    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/74.0.3729.131 Safari/537.36',
        'Accept':
            'text/html,'
            'application/xhtml+ xml,application/xml;q = 0.9,'
            'image/webp,image/apng,*/*;q=0.8, application/signe-exchange;v = b3',
        'Host':
            'www.ximalaya.com'
    }

    sign = exec_js(headers)
    headers["xm-sign"] = sign

    link = requests.get(url, headers=headers).text
    link_dict = json.loads(str(link))

    return link_dict


# 主逻辑
def main():
    track_list = []

    data_list = get_link(URL).get("data").get("tracksAudioPlay")

    for index, source in enumerate(data_list, 1):
        only_name = uuid4()
        track_title = source.get("trackName")

        track_cover_url = source.get("trackCoverPath")
        track_cover_url = f"http:{track_cover_url}"
        album_name = source.get("albumName")
        track_url = source.get("src")

        # 获取封面文件
        track_cover_name = f"{only_name}.jpg"
        track_cover_path = os.path.join(COVER_PATH, track_cover_name)
        cover_source = requests.get(track_cover_url)
        with open(track_cover_path, "wb") as f:
            f.write(cover_source.content)

        # 获取音乐文件
        track_name = f"{only_name}.mp3"
        track_path = os.path.join(MUSIC_PATH, track_name)
        track_source = requests.get(track_url)
        with open(track_path, "wb") as f:
            f.write(track_source.content)

        time.sleep(0.5)
        print(f"已下载第{index}个资源")

        # 音乐信息
        track_info = {
            "track_title": track_title,
            "track_name": track_name,
            "track_cover_name": track_cover_name,
            "album_name": album_name
        }

        track_list.append(track_info)

    start_mongodb_cmd = r"start mongod -fD:\Basic_support\MongoDB\mongod.conf"
    os.system(start_mongodb_cmd)
    DB.Source.insert_many(track_list)

    return {"status": True}


if __name__ == "__main__":
    result = main()
    if result:
        print("完成!")
