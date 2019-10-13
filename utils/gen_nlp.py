import os

import jieba
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities

from config import DB

# CDM 命令, 以配置文件开启 MongoDB
start_mongodb_cmd = r"start mongod -fD:\Basic_support\MongoDB\mongod.conf"
# CDM 命令, 以配置文件开启 Redis
start_redis_cmd = r"start redis-server"
# 执行 CDM 命令
os.system(start_mongodb_cmd)
os.system(start_redis_cmd)

content_list = list(DB.Source.find({}))

all_doc_list = []  # 匹配项分词结果集
for doc in content_list:  # 进行分词, 充实匹配项内容
    doc_list = list(jieba.cut_for_search(doc.get("track_title")))  # 利用 jieba 分词
    all_doc_list.append(doc_list)  # 将分词结果追加到匹配项分词结果集

dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
# 生成 lsi 模型训练结果
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]  # 利用匹配项分词结果集生成 corpus 语料库
lsi = models.LsiModel(corpus)  # corpus 语料库的 lsi 模型训练结果

#  利用稀疏矩阵计算相似度, 将语料库 corpus 的训练结果作为初始值
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))


def my_nlp_content(q):
    doc_test_list = list(jieba.cut_for_search(q))  # 用户表达分词结果集
    # 利用用户表达分词结果集生成 doc_test_vec 语料库, 用于与初始值做矩阵相似度计算
    doc_test_vec = dictionary.doc2bow(doc_test_list)

    sim = index[lsi[doc_test_vec]]  # 矩阵相似度计算

    cc = sorted(enumerate(sim), key=lambda item: -item[1])  # 根据相似度结果排序 (降序)
    if cc[0][1] >= 0.618:  # 限制最低相似度
        content = content_list[cc[0][0]]  # 相似度最高项的下标即 content_list 中 (计算得出的) 最佳匹配项的下标
        # print(text)
        return content  # 返回匹配项元素
