# aiToyPro

该项目旨在设计一款借助于 Flask + 人工智能实现的语音互动亲子玩具, 
面向 3-5 岁幼年儿童, 在为幼年儿童提供优质音频内容的基础上构建幼儿社交圈, 
通过音频交友, 进行交流分享与学习. 同时支持 APP 远程内容管理, 消息推送, 内容推送, 
好友管理等基本功能

### 项目应用技术以及技术实现功能

- Flask (项目框架)
    - 登录注册相关
        - reg  注册
        - login  登录
        - auto_log  自动登录
    - 内容相关
        - content_list  获取内容信息
        - get_cover  获取封面
        - get_music  获取资源
    - 语音消息及音频上传相关
        - app_uploader  App 向 Toy 发送语音消息
        - toy_uploader  Toy 向 App 发送语音消息
        - ai_uploader  Toy 向 AI 发送语音指令
    - 硬件设备及二维码相关
        - scan_qr  扫描二维码
        - bind_toy  绑定玩具
        - toy_list  展示玩具列表
        - get_qr  获取二维码图片
    - 好友通讯录相关
        - friend_list  好友列表展示
        - add_req  处理好友添加请求
        - req_list  展示好友请求列表
        - acc_req  同意好友请求
        - ref_req  拒绝好友请求
- WebSocket
    - APP 通讯
    - Toy 通讯
- NLP
    - 语音内容 (转文字) 相似度匹配

### 功能简述

- app
    - 推送语音消息给 Toy
    - 推送音乐等语音内容给 Toy
    - 与 Toy 进行相互之间的语音交流
    - 管理好友
    - 管理 Toy
- toy
    - 主动请求音乐等语音内容
    - 与 APP 进行相互之间的语音交流
    - 与 AI 进行交互
    - Toy 之间进行相互之间的语音交流