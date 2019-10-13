import os  # 执行 CND 命令 os.system(CMD)
import time  # 生成当前时间
import hashlib  # 摘要算法
from uuid import uuid4  # 生成随机字符串

import requests  # Python 处理网络请求的第三方库

# Begin --> 从配置文件中导入相关变量
from config import DB
from config import LT_URL
from config import QRCODE_PATH
# <-- End


# 生成设备二维码
def create_device_d2code(num):
    device_list = []  # 暂时存储设备唯一码的数据结构
    """
    device_list = [
        {"device_key": d2_str}
        ...
    ]
  """

    for index in range(1, num+1):  # 生成指定数量的设备唯一码
        # 通过自定义加密规则生成设备唯一码
        d2_str = hashlib.md5(f"{uuid4()}{time.time()}{uuid4()}".encode("UTF-8")).hexdigest()
        device_info = {"device_key": d2_str}

        device_list.append(device_info)

        d2_picture = requests.get(LT_URL % d2_str)  # 调用联图二维码 API 返回二维码图片数据流
        d2_path = os.path.join(QRCODE_PATH, f"{d2_str}.jpg")  # 拼接二维码图片保存路径, 以设备唯一码.jpg 命名
        with open(d2_path, "wb") as f:  # 持久化
            f.write(d2_picture.content)

        print(f"已生成第{index}个设备码")

    start_mongodb_cmd = r"start mongod -fD:\Basic_support\MongoDB\mongod.conf"
    os.system(start_mongodb_cmd)
    DB.Devices.insert_many(device_list)

    return {"status": True}


if __name__ == "__main__":
    result = create_device_d2code(10)
    if result:
        print("完成!")
