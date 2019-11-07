# -*-coding:utf-8 -*-
# 根据新闻id推送相似的新闻列表
import gensim
import numpy as np
from operator import itemgetter
from . import CommonMethod
from .define import w2v_path_model
import random

# 加载进训练好的模型
model = gensim.models.Word2Vec.load(w2v_path_model)
#model = ''


def similar_news(news_id):
    # 根据id确定数据表和新闻id
    table, number = CommonMethod.get_table_and_id(news_id)
    mymodels = CommonMethod.table_to_models(table)
    try:
        news_info = mymodels.objects.filter(id=number).values('keywords', 'label')[0]
    except:
        news_info = None
    if news_info:
        keywords = news_info['keywords']
        label = news_info['label']
    else:
        return []
    # 先计算当前新闻的词向量
    cur_vec = cal_d2v(' '.join(' '.join(keywords)))

    # 根据label去查找相似的新闻
    news_data = mymodels.objects.filter(label=label).order_by('-time')[:100].values_list('id', 'time', 'source', 'img',
                                                                                         'keywords')
    temp_list = []
    for one_news in news_data:
        news_id = one_news[0]
        if news_id != number:
            simile_score = xiangsidu(cur_vec, cal_d2v(' '.join(one_news[4])))
            temp_dict = {}
            temp_dict['news_id'] = str(mymodels._meta.db_table) + '_' + str(one_news[0])
            temp_dict['news_time'] = str(one_news[1])
            temp_dict['news_source'] = CommonMethod.get_short_source(mymodels, one_news[2])
            temp_dict['news_img'] = one_news[3]
            temp_dict['news_score'] = simile_score
            temp_list.append(temp_dict)
    # 只要有相似新闻就返回，但是数量不超过五条
    after_rank_temp_list = sorted(temp_list, key=itemgetter('news_score'), reverse=True)
    if len(after_rank_temp_list) > 5:
        return after_rank_temp_list[:5]
    else:
        return after_rank_temp_list


def cal_d2v(words):
    '''
    :param words: 一个列表
    :return: 通过词向量，加权平均值求句子的向量
    '''
    sum_vec = []
    for word in words:
        try:
            word2vec = model[word]
            sum_vec.append(word2vec)
        except:
            continue
    if sum_vec != []:
        doc2vec = np.mean(sum_vec, axis=0)  # 计算每一列的均值
    else:
        doc2vec = ""
    return doc2vec


def cal_cos(a_vec, b_vec):
    '''
    :param a_vec:
    :param b_vec:
    :return: 计算两个输入向量直接的cosine similarity
    '''
    a_vec = np.array(a_vec)
    b_vec = np.array(b_vec)
    l1 = np.sqrt(a_vec.dot(a_vec))
    l2 = np.sqrt(b_vec.dot(b_vec))
    cos_sim = float(a_vec.dot(b_vec) / (l1 * l2))
    return cos_sim


# 传入两个向量·，计算两个向量的cos
def xiangsidu(a_text_d2v, b_text_d2v):
    print('****')
    print(a_text_d2v, b_text_d2v)
    if a_text_d2v == "" or b_text_d2v == "":
        return 0
    else:
        return cal_cos(a_text_d2v, b_text_d2v)
