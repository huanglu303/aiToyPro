# 数据库配置
from redis import Redis
from pymongo import MongoClient  # Python 操作 MongoDB 的第三方库

client_mongodb = MongoClient()  # 为空则默认为 localhost 27017
DB = client_mongodb["AiToy"]
RDB = Redis("127.0.0.1", 6379, db=4)

# url 路径配置(资源爬取)
URL = "https://www.ximalaya.com/revision/play/album?albumId=245037&pageNum=1&sort=1&pageSize=30"

# Begin --> 目录配置
COVER_PATH = "Cover"
MUSIC_PATH = "Music"
QRCODE_PATH = "Qrcode"
RECOFILE_PATH = "RecoFile"
# <-- End

# RET返回值
RET = {
    "CODE": 0,
    "MSG": "注册成功",
    "DATA": {}
}

# 联图二维码接口API(将 %s 内容生成二维码图片, 返回数据流)
LT_URL = "http://qr.topscan.com/api.php?text=%s"

# 需填入百度AI个人项目的相关信息
APP_ID = ""
API_KEY = ""
SECRET_KEY = ""

# 需填入图灵机器人TL_API_KEY
TL_API_KEY = ""
