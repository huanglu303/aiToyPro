import json

from config import RDB


# 存储未读消息
def set_redis(to_user, from_user):
    to_user_json = RDB.get(to_user)  # 通过 to_user 查询 Redis 中的数据
    if to_user_json:  # 若存在
        to_user_dict = json.loads(to_user_json)  # 反序列化

        #######
        # if to_user_dict.get(from_user):  # 若获取的数据结构中包含 from_user 的数据
        #     to_user_dict[from_user] += 1  # 加 1
        # else:  # 否则
        #     to_user_dict[from_user] = 1  # 添加记录
        #######

        # 优化代码方案:
        to_user_dict[from_user] = to_user_dict.get(from_user, 0) + 1

        to_user_json = json.dumps(to_user_dict)  # 重新序列化 赋值(覆盖)
    else:  # 若不存在
        to_user_json = json.dumps({from_user: 1})  # 序列化 1 条数据 赋值(覆盖)

    RDB.set(to_user, to_user_json)  # 将结果添加到 Redis 数据库中 存储 1 条未读数据


# 获取单个用户的未读消息
def get_redis(to_user, from_user):
    to_user_json = RDB.get(to_user)
    if to_user_json:
        to_user_dict = json.loads(to_user_json)

        #######
        # count = to_user_dict.get(from_user)
        # if not count:
        #     count = 0
        # to_user_dict[from_user] = 0
        #######

        # 优化方案?
        count = to_user_dict.pop(from_user, 0)
        to_user_json = json.dumps(to_user_dict)
    else:
        to_user_json = json.dumps({from_user: 0})
        count = 0

    RDB.set(to_user, to_user_json)

    return count


# 获取玩具的所有未读消息
def get_redis_toy(to_user, from_user):
    to_user_json = RDB.get(to_user)
    if to_user_json:
        to_user_dict = json.loads(to_user_json)
        count = to_user_dict.pop(from_user, 0)
        if count == 0:
            for key, value in to_user_dict.items():
                if value:
                    from_user = key
                    count = value
        to_user_dict[from_user] = 0

        to_user_json = json.dumps(to_user_dict)
    else:
        to_user_json = json.dumps({from_user: 0})
        count = 0

    RDB.set(to_user, to_user_json)

    return count, from_user


# 获取所有未读消息
def get_all_redis(to_user):
    to_user_json = RDB.get(to_user)
    if to_user_json:
        to_user_dict = json.loads(to_user_json)
        to_user_dict["count"] = sum(to_user_dict.values())
    else:
        to_user_dict = {"count": 0}

    return to_user_dict
