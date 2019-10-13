from flask import Flask  # 导入 Flask 类
from flask_cors import CORS  # Flask 解决跨域问题的第三方模块 Access-Control-Allow-Origin: *

# 蓝图 处理 "/reg" "/login" "/auto_login" 等接口
from serv.users_api import user_blue
# 蓝图 处理 "/chat_list" "/recv_msg" "/get_chat/<chat_name>" 等接口
from serv.chat_api import chat_blue
# 蓝图 处理 "/friend_list" 等接口
from serv.friends_api import friends_blue
# 蓝图 处理 "/scan_qr" "/bind_toy" "/toy_list" "/get_qr/<filename>" "/open_toy" 等接口
from serv.devices_api import device_blue
# 蓝图 处理 "/content_list" "/get_cover/<filename>" "/get_music/<filename>" 等接口
from serv.contents_api import content_blue
# 蓝图 处理 "/app_uploader" "/toy_uploader" "/ai_uploader" 等接口
from serv.uploader_api import uploader_blue


app = Flask(__name__)  # 实例化 Flask 对象(应用)

# Begin --> 注册蓝图
app.register_blueprint(user_blue)
app.register_blueprint(chat_blue)
app.register_blueprint(friends_blue)
app.register_blueprint(device_blue)
app.register_blueprint(content_blue)
app.register_blueprint(uploader_blue)
# <-- End

# 使用 Flask 第三方跨域解决方案
CORS(app)

if __name__ == "__main__":  # 执行本文件
    # 启动 Flask 应用, 监听本机所有 IP 的 9000 端口
    app.run("0.0.0.0", 9000)
