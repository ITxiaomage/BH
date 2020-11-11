from django.shortcuts import render
from django.http import HttpResponse
from . import spider
from . import initData
from . import handle_cast
from .organiza import *
from .mongo import *
from .calSimilarNews import *
from datetime import datetime, timedelta
from operator import itemgetter
import json
from simhash import Simhash
from django.db.models import Q
from . import CommonMethod,dfkxSpider
from functools import reduce
import re


####################################定时任务#########################
from apscheduler.scheduler import Scheduler

sched_1 = Scheduler()  # 实例化，固定格式
sched_2 = Scheduler()  # 实例化，固定格式


#  8个小时更新一次
@sched_1.interval_schedule(hours=8)
def mytask_1():
    print('定时任务启动,时间为：{0}'.format(datetime.now().strftime("%Y-%m-%d")))
    # 科协一家
    #update_kxyj_data()
    # 中央新闻
    #update_china_top_news()
    # 科协官网
    update_kexie_news_into_mysql()

    # 人名网时政
    updata_get_rmw_news_data()
    # 人民网科技
    #update_get_rmw_kj_data()
    #疫情防控
    #dfkxSpider.yqfk()
    print('定时任务结束,时间为：{0}'.format(datetime.now().strftime("%Y-%m-%d")))


#  每天更新一次
@sched_2.interval_schedule(hours=12)
def mytask__2():
    print('定时任务启动,时间为：{0}'.format(datetime.now().strftime("%Y-%m-%d")))
    # # cast数据库
    hanle_cast_into_mysql()
    dfkxSpider.start_dfkx_spider()
    print('定时任务结束,时间为：{0}'.format(datetime.now().strftime("%Y-%m-%d")))


sched_1.start()  # 启动该脚本
sched_2.start()  # 启动该脚本


def example(request):
    dfkxSpider.start_gxkx_spider()
    news_list = []
    #news_list.append(spider.china_top_news())
    #dfkxSpider.yqfk()
    #hanle_cast_into_mysql()
    # 科协一家
    #update_kxyj_data()
    # 中央新闻
    #update_china_top_news()
    # 科协官网
    update_kexie_news_into_mysql()
    # 人名网时政
    updata_get_rmw_news_data()
    # 人民网科技
    #update_get_rmw_kj_data()
    hanle_cast_into_mysql()
    dfkxSpider.start_dfkx_spider()
    return HttpResponse('success')
    # context = {"news_list":news_list}
    # return render(request,'news.html', context)


#########################根据用户id、department和用户记录返回新闻列表###############
def get_user_news_list(request):
    # 获取频道错误就设置第一个频道
    try:
        channel = request.GET.get('channel')
        print("current channel:{0}:".format(channel))
        # if channel not in get_all_channel():
        #     channel = ChannelToDatabase.objects.all().values_list('channel')[0][0]
    except Exception as err:
        channel = ChannelToDatabase.objects.all().values_list('channel')[0][0]
        print("获取频道出现错误，因此设为默认值:{0}".format(channel))
        #print(err)

    try:
        flag = request.GET.get('flag')
        if not flag:
            flag=0
    except Exception as err:
        flag = 0
        #print('获取num错误')
        #print(err)

    # 地方科协和学会登录时，会增加一个单独的首页
    try:
        main = request.GET.get('main')
        if not main:
            main = 0
    except  Exception as e:
        main = 0

    # 获取用户id
    try:
        user_id = request.GET.get('user_id')
    except Exception as err:
        print("获取用户id出现错误")
        user_id = None
        #print(err)
    # 临时修改为默认用户
    if not user_id:
        user_id = '999'
    # 获取用户department列表
    try:
        department = request.GET.get('department')
        if department:
            department = json.loads(department)
        else:
            department=[]
    except Exception as err:
        print("获取用户department列表出现错误")
        department = []
        print(err)
    # 有用户id就按照用户id推送，并进行用户画像记录
    result_list = accord_user_id_get_news_list(user_id, department, channel, flag,main)
    # else:  # 没有用户id,就按照部门推送，不进行用户画像记录
    #     result_list = channel_branch(channel, branch, flag)
    return HttpResponse(json.dumps(result_list, ensure_ascii=False))


# 根据用户id和department和channel获取到新闻推荐的列表
def accord_user_id_get_news_list(user_id, department, channel, flag, main=0):
    # 在时政要闻和科技热点进行个性化推荐
    #有空需要进行解耦，频道的名称应该只有数据库有
    if channel == CHANNEL_SZYW: # 时政要闻
        result_list = individual(user_id, channel, News, LB=True)#暂时设置全部是带图片的
    elif channel == CHANNEL_KJRD: # 科技热点
        result_list = individual(user_id, channel, TECH, LB=True)
    # 中国科协
    elif channel == CHANNEL_ZGKX:
        result_list = search_kx_data_from_mysql(flag)
    # 当前频道为全国学会，并且用户department有学会，就按照department，否则按时间检索
    elif channel == CHANNEL_QGXH:
        print("开始进入全国学会函数")
        result_list = get_qgxh_news_list(department,main)

    # 当前频道为地方科协，并且用户department有地方科协，就就按照department，否则按时间检索
    elif channel == CHANNEL_DFKX:
        result_list = get_dfkx_news_list(department,main)
    elif channel == '战役防控':
        result_list = get_zyfk_news()
    else :
        result_list = []
    return result_list


### 额外增加的战役防控查找
def get_zyfk_news():
    result_list = []
    temp_dict ={}
    #重要发布
    temp_dict['重要发布'] = sorted(search_zyfk_news(source='重要发布'), key=itemgetter('priority', 'news_time'), reverse=True)

    #科协要闻
    temp_dict['科协要闻'] = sorted(search_zyfk_news(source='科协要闻'), key=itemgetter('priority', 'news_time'), reverse=True)
    #两翼联动
    temp_list =[]
    temp_list.extend(sorted(search_zyfk_news(source='全国学会'), key=itemgetter('priority', 'news_time'), reverse=True))
    temp_list.extend(sorted(search_zyfk_news(source='地方科协'), key=itemgetter('priority', 'news_time'), reverse=True))
    temp_dict['两翼联动'] = temp_list
    #应急科普
    temp_dict['应急科普'] = sorted(search_zyfk_news(source='应急科普'), key=itemgetter('priority', 'news_time'), reverse=True)
    #答疑解惑
    temp_dict['答疑解惑'] = sorted(search_zyfk_news(source='答疑解惑'), key=itemgetter('priority', 'news_time'), reverse=True)
    #抗疫榜样
    temp_dict['抗疫榜样'] = sorted(search_zyfk_news(source='抗疫榜样'), key=itemgetter('priority', 'news_time'), reverse=True)
    #媒体报道
    temp_dict['媒体报道'] = sorted(search_zyfk_news(source='媒体报道'), key=itemgetter('priority', 'news_time'), reverse=True)
    # banners轮播图
    temp_dict['banners'] = search_zyfk_news(LB=True)

    return temp_dict

def search_zyfk_news(id__list=[],source=None,n = 3,LB =False):
    result =[]
    if LB:
        try:
            data = YQFK.objects.exclude(id__in=id__list).filter(~Q(img=None)).filter(~Q(img='')).filter(
                ~Q(img=' ')).values_list('id', 'title', 'img', 'time',
                                         'source', 'priority').order_by('-time')[:n]
        except:
            pass
    else:
        try:
            data = YQFK.objects.filter(hidden=1).exclude(id__in=id__list).filter(source=source).values_list('id',
                                                                                                               'title',
                                                                                                               'img',
                                                                                                               'time',
                                                                                                               'source',
                                                                                                               'priority',
                                                                                                               ).order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(YQFK._meta.db_table))
            print(err)


    if data:
        for one in data:
            temp_dict = {}
            news_id = str(YQFK._meta.db_table) + '_' + str(one[0])
            temp_dict['news_id'] = news_id
            temp_dict['news_title'] = one[1]

            # 在这里要进行img
            temp_dict['news_img'] = CommonMethod.get_correct_img(one[2])
            temp_dict['news_time'] = str(one[3])
            temp_dict['news_source'] = one[4]
            temp_dict['priority'] = one[5]
            result.append(temp_dict)

    return result

# 个性化推荐算法
def individual(user_id, channel, mymodel,LB=None):
    result_list = []
    # 先检测用户是否存在，不存在就创建新的用户，按照时间返回新闻
    user = search_user_from_momgodb(id=user_id)

    if not user:
        create_new_user_in_mongo(user_id)
        # 如果没有此用户，则创建新的用户

        # 用户不存在就按照检索10条数据create_new_user_in_mongo
    if not user or user_id == '999':
        return accord_label_get_news(mymodel, LB)  # 暂时设置全部图片

    # 有用户就根据用户画像检索新闻
    user_images_dict = get_user_images_accord_user_id_channel(user_id, channel)
    result_list.extend(get_news_list_accord_user_images(mymodel, user_images_dict))
    return limit_ten_news(result_list)


# 数据库的种类都查询10条 排序返回
def accord_label_get_news(mymodels, LB=None):
    result_list = []
    result_list.extend(search_data_from_mysql(mymodels, MAX_SEARCH_NEWS, LB=LB))

    temp_list = sorted(result_list, key=itemgetter('priority', 'news_time'), reverse=True)
    return limit_ten_news(temp_list)


def limit_ten_news(news_list):
    if len(news_list) > MAX_NEWS_NUMBER:
        return news_list[:MAX_NEWS_NUMBER]
    return news_list


# 根据用户画像返回一个新闻列表
def get_news_list_accord_user_images(mymodels, user_images_dict):
    """
    :param mymodels:模型类
    :param user_images_dict: 用户画像的字典
    :return: 新闻列表
    """
    result_list = []
    label_list = user_images_dict['labelList']
    label_list = sorted(label_list, key=itemgetter('flag'), reverse=True)
    if len(label_list) > MAX_NEWS_NUMBER:
        label_list = label_list[:MAX_NEWS_NUMBER]
    id_list = []
    if label_list:
        for one_label in label_list:
            label = one_label['label']
            score = one_label['score']
            # 计算label的词向量
            label_vec = cal_d2v(label)
            # 获取候选新闻列表，根据新闻id获取新闻详情，然后计算相似性  暂时只检索有图片的新闻
            first_news_list = search_data_from_mysql(mymodels, MAX_SEARCH_NEWS, LB=True)
            for one_news in first_news_list:
                news_id = one_news['news_id']
                news_info = accord_news_id_get_content_list(news_id)
                news_keywords = news_info["keywords_list"].split(' ')
                if not news_keywords:
                    continue
                news_keywords_vec = cal_d2v(news_keywords)
                # 相似性大于0.8以上就认为是同一篇文章，相似性小于0.2就认为相似性太低，就不需要了，找到最相似的前10篇文章
                similar_score = xiangsidu(news_keywords_vec, label_vec)
                if SIMILIAR > similar_score > MIN_SIMILIAR:
                    # 这里的规则为相似性*10 +score得分
                    news_score = similar_score * 10 + score
                    one_news['news_score'] = news_score
                    if news_id in id_list:
                        continue
                    id_list.append(news_id)
                    result_list.append(one_news)
    if result_list:
        # 先按优先级，然后按照时间排序，然后按照相似性排序
        second_result_list = sorted(result_list, key=itemgetter('priority', 'news_time', 'news_score'), reverse=True)
    else:
        second_result_list = []

    final_result_list = list_dict_duplicate_removal(second_result_list)
    # 在这里将结果利用simhash去重
    # final_result_list.extend(simhash_remove_similar(second_result_list))
    print('通过用户画像返回的新闻列表长度:{0}'.format(len(final_result_list)))
    if len(final_result_list) < MAX_NEWS_NUMBER:
        get_enough_news(final_result_list, mymodels)

    final_result_list = sorted(final_result_list, key=itemgetter('priority', 'news_time'), reverse=True)

    print('补充数据返回的新闻列表长度:{0}'.format(len(final_result_list) - len(final_result_list)))
    return final_result_list


def list_dict_duplicate_removal(data_list):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)


# simhash算法去重
def simhash_remove_similar(news_list):
    result_list = []
    # 需要两两比较simhash值
    len_news_list = len(news_list)
    for i in range(len_news_list):
        news_i_id = news_list[i]['news_id']
        news_i_news_content = accord_news_id_get_content_list(news_i_id)['news_content']
        sim_hash1 = Simhash(news_i_news_content)
        for j in range(i + 1, len_news_list):
            # 已经被打过标记的不判断
            if 'del' in news_list[j]:
                continue
            news_j_id = news_list[j]['news_id']
            news_j_news_content = accord_news_id_get_content_list(news_j_id)['news_content']
            sim_hash2 = Simhash(news_j_news_content)
            # 如果两个新闻的汉明距离小于 10 则按照顺序只保留一个
            if sim_hash1.distance(sim_hash2) <= SIMHASH_DISTINCT:
                # 表示不要这个新闻了
                news_list[j]['del'] = 'yes'
    for news in news_list:
        if 'del' not in news:
            result_list.append(news)
    return result_list


# # 中国科协频道算法
# def get_zgkx_news_list():
#     # 找到mysql中科协领导人
#     kx_leaders_list = get_kx_leaders_from_mysql()
#     # 从数据库取出最新的数据
#     news_list = search_data_from_mysql(KX, MAX_SEARCH_NEWS)
#     # 如果取到的日期和当前的日期之间相差7天以上就删除
#     recent_news_list = diff_time(news_list)
#
#     # 检索出科协领导人的新闻，然后按照时间排序,得到第一次的新闻推荐列表
#     first_news_list = sort_kx_news(news_list=recent_news_list, keywords_list=kx_leaders_list)
#
#     # 科协领导人的新闻最多三条
#     if len(first_news_list) > 3:
#         first_news_list = first_news_list[:3]
#     else:
#         first_news_list = first_news_list
#     final_result_list = []
#     while True:
#         # 在这里将结果利用simhash去重
#         final_result_list.extend(simhash_remove_similar(first_news_list))
#         #新闻数量不够就一直补充
#         if len(final_result_list)  < MAX_NEWS_NUMBER:
#             get_enough_news(final_result_list,KX)
#         else:
#             break
#     return final_result_list


# 找出news_list中包含科协领导人的新闻，并返回
def sort_kx_news(news_list, keywords_list):
    result_list = []
    for one_news in news_list:
        news_id = one_news['news_id']
        # 根据新闻id获取到新闻的详情
        news_info_dict = accord_news_id_get_content_list(news_id)
        for name in keywords_list:
            title = news_info_dict['news_title']
            content = news_info_dict['news_content']
            if name in title or name in content:
                score = title.count(name) * 10 + content.count(name)
                one_news['news_score'] = score
            else:
                one_news['news_score'] = 0
        result_list.append(one_news)
    # 按照时间排序,然后按照得分排序
    final_result_list = sorted(result_list, key=itemgetter('priority', 'news_time', 'news_score'), reverse=True)
    return final_result_list


# 获取科协领导人
def get_kx_leaders_from_mysql():
    result_list = []
    try:
        data = KxLeaders.objects.filter(hidden=1).values_list('name')
    except Exception as err:
        data = None
        print("{0}数据库检索不到数据".format(KxLeaders._meta.db_table))
        print(err)
    if data:
        for one in data:
            result_list.append(one[0])
    return result_list


# 全国学会频道推荐算法
def get_qgxh_news_list(department=[],main=0):
    qgxh_dep_numben_list = num_xuehui()
    result_list = []
    source_list =[]
    #department不为空
    if main==str(1):
        # 找到用户兼职的所有全国学会单位，并根据这些单位去检索新闻。
        for one_dep in department:
            one_dep = str(one_dep)
            if one_dep in qgxh_dep_numben_list:
                source = accord_number_get_department(one_dep)
                result_list.extend(search_data_from_mysql(QGXH, source=source))
        # 如果result_list为空，说明用户没有在全国学会兼职，那么返回数据库最新的新闻
        if not result_list:
             result_list = sorted(search_data_from_mysql(QGXH), key=itemgetter('priority', 'news_time'), reverse=True)

    else:
        print("进行检索")
        for one in qgxh_dep_numben_list:
            if int(one) not in department:
                source_list.append(one)
        for source in source_list:
            result_list.extend(search_data_from_mysql(QGXH,n=1,source=source))
    #优先级排序处理
    result_list = sorted(result_list, key=itemgetter('priority', 'news_time'), reverse=True)

    if len(result_list) < MAX_NEWS_NUMBER:
        get_enough_news(result_list, QGXH)
        print("检索的数据总量为{0}".format(len(result_list)))
        result_list = sorted(result_list, key=itemgetter('priority', 'news_time'), reverse=True)
        for i in result_list:
            print(i['title'])
        return result_list[:MAX_NEWS_NUMBER]
    else:
        return result_list[:MAX_NEWS_NUMBER]


# 地方科协频道推荐算法
def get_dfkx_news_list(department=[], main=0):
    dfkx_dep_numben_list = num_dfkx()
    result_dict = {}
    label_one =[]
    label_two = []
    label_three = []
    lb_news = []
    source_list=[]
    if main == str(1): # 首页是根据source获取的
        # 找到用户兼职的所有地方科协单位，并根据这些单位去检索新闻。
        for one_dep in department:
            one_dep = str(one_dep)
            if one_dep in dfkx_dep_numben_list:
                source = accord_number_get_department(one_dep)
                source = AgencyDfkx.objects.filter(department=source)[0]
                # 每个部门都需要检索标签为1.2.3的新闻资讯
                label_one.extend(search_data_from_mysql(myModel=DFKX, n=MAX_NEWS_NUMBER,source=source, label=1))
                #这个新闻必须有图片
                label_two.extend(search_data_from_mysql(myModel=DFKX, n = MAX_NEWS_NUMBER,source=source,label=2, LB=True))
                label_three.extend(search_data_from_mysql(myModel=DFKX, n =MAX_NEWS_NUMBER,source=source,label=3))

        # 如果最基本的3条新闻都没有，那就随便补充新闻了
        if len(label_one) < LIMIT_NEWS:
            id_list = []
            id_list.extend(get_news_id(label_one))
            label_one.extend(search_data_from_mysql(myModel=DFKX, id__list=id_list, n=LIMIT_NEWS, label=1))

        # 必须要有图
        if len(label_two) < LIMIT_NEWS:
            id_list = []
            id_list.extend(get_news_id(label_two))
            label_two.extend(
                search_data_from_mysql(myModel=DFKX, id__list=id_list, n=LIMIT_NEWS, label=2, LB=True))

        if len(label_three) < LIMIT_NEWS:
            id_list = []
            id_list.extend(get_news_id(label_three))
            label_three.extend(
                search_data_from_mysql(myModel=DFKX, id__list=id_list, n=LIMIT_NEWS, label=3))
        # 然后排序
        label_one = sorted(label_one, key=itemgetter('priority', 'news_time'), reverse=True)
        label_two = sorted(label_two, key=itemgetter('priority', 'news_time'), reverse=True)
        label_three = sorted(label_three, key=itemgetter('priority', 'news_time'), reverse=True)

        # 然后裁剪
        if len(label_one) > LIMIT_NEWS:  # 在这里一般只会超出臭猪，
            label_one = label_one[:LIMIT_NEWS]
        if len(label_two) > LIMIT_NEWS:  # 在这里一般只会超出臭猪，
            label_two = label_two[:LIMIT_NEWS]

        if len(label_three) > LIMIT_NEWS:  # 在这里一般只会超出臭猪，
            label_three = label_three[:LIMIT_NEWS]

        # 找轮播图,把已经出现的新闻过滤掉
        id_list = []
        id_list.extend(get_news_id(label_one))
        id_list.extend(get_news_id(label_two))
        id_list.extend(get_news_id(label_three))
        for one_dep in department:
            one_dep = str(one_dep)
            if one_dep in dfkx_dep_numben_list:
                source = accord_number_get_department(one_dep)
                source = AgencyDfkx.objects.filter(department=source)[0]
                lb_news.extend(search_data_from_mysql(myModel=DFKX, n=MAX_NEWS_NUMBER, source=source, id__list=id_list, LB=True))
        #还是不够，就不在乎source，只需要有图就行
        if len(lb_news) < LIMIT_NEWS:
            lb_news.extend(search_data_from_mysql(myModel=DFKX, n=LIMIT_NEWS, id__list=id_list, LB=True))

    else: #main == 0 时，地方科协需要排除原始的source

        for one in dfkx_dep_numben_list:
            if int(one) not in department:
                source_list.append(one)

        #对于每一个source_list里面的都检索一条新闻
        for source in source_list:
            source_ = accord_number_get_department(source)
            _source = AgencyDfkx.objects.filter(department=source_)[0]
            label_one.extend(search_data_from_mysql(myModel=DFKX, n = 1, label=1,source=_source))
            #这个新闻必须有图片
            label_two.extend(search_data_from_mysql(myModel=DFKX, n = 1,label=2, LB=True,source=_source))
            label_three.extend(search_data_from_mysql(myModel=DFKX, n =1,label=3,source=_source))



        # 然后排序
        label_one = sorted(label_one, key=itemgetter('priority', 'news_time'), reverse=True)
        label_two = sorted(label_two, key=itemgetter('priority', 'news_time'), reverse=True)
        label_three = sorted(label_three, key=itemgetter('priority', 'news_time'), reverse=True)

        # 然后裁剪
        if len(label_one) > LIMIT_NEWS:  # 在这里一般只会超出臭猪，
            label_one = label_one[:LIMIT_NEWS]
        if len(label_two) > LIMIT_NEWS:  # 在这里一般只会超出臭猪，
            label_two = label_two[:LIMIT_NEWS]

        if len(label_three) > LIMIT_NEWS:  # 在这里一般只会超出臭猪，
            label_three = label_three[:LIMIT_NEWS]

        # 找轮播图,把已经出现的新闻过滤掉
        id_list = []
        id_list.extend(get_news_id(label_one))
        id_list.extend(get_news_id(label_two))
        id_list.extend(get_news_id(label_three))
        #
        lb_news.extend(search_data_from_mysql(myModel=DFKX, n=LIMIT_NEWS, id__list=id_list, LB=True))
        #如果恰好没有，就只能用source 的了

        lb_news = sorted(lb_news, key=itemgetter('priority', 'news_time'), reverse=True)


    if len(lb_news)>LIMIT_NEWS: #在这里一般只会超出臭猪，
        lb_news = lb_news[:LIMIT_NEWS]

    #包装返回
    result_dict['banners'] = lb_news #轮播图
    result_dict['news'] = label_one # 新闻
    result_dict['local'] = label_two #地方动态
    result_dict['provincial'] = label_three #学会

    return result_dict


# 得到已经检索的新闻id
def get_news_id(news_list):
    id_list = []
    for one_news in news_list:
        news_id = one_news['news_id']
        index = news_id.rindex("_")
        number = news_id[index + 1:]
        id_list.append(int(number))
    return id_list

# 根据部门和频道获
def channel_branch(channel, branch, flag=0):
    result_list = []
    # 根据频道得到数据库表名
    db_table = ChannelToDatabase.objects.filter(channel=channel).values_list('database')
    # 根据数据库表名获取到模型
    mymodels = CommonMethod.table_to_models(db_table[0][0])

    # 中国科协的频道单独推送
    # 如果是中国科协频道，那么必须由三部分组成：要闻、视频和通知
    if channel == CHANNEL_ZGKX:
        return search_kx_data_from_mysql()

    # 全国学会的用户在全国学会频道应该就只有他们自己的新闻，地方科协也一样
    if branch in num_xuehui() and channel == CHANNEL_QGXH:
        # 根据部门ID取得部门名称
        department = accord_number_get_department(branch)
    elif branch in num_dfkx() and channel == CHANNEL_DFKX:
        department = accord_number_get_department(branch)
    else:
        department = None
    # 将部门名称作为条件去查询，要不然就默认按照时间
    result_list.extend(search_data_from_mysql(mymodels, n=MAX_SEARCH_NEWS, source=department))

    # 如果取到的日期和当前的日期之间相差7天以上就删除
    recent_news_list = diff_time(result_list)

    # 按照当前用户的id，检索用户的历史记录，将得到的新闻进行算法排序,得到第一次的新闻推荐列表
    sort_all_news(news_list=recent_news_list, branch=branch, channel=channel)

    # 检测新闻数量是否足够，如果不够就在补充到足够的数量,得到第二个新闻推荐列表
    get_enough_news(recent_news_list, mymodels)
    if len(recent_news_list) >= MAX_NEWS_NUMBER:
        final_result_list = recent_news_list[:MAX_NEWS_NUMBER]
    else:
        final_result_list = recent_news_list
    return final_result_list


# 搜索科协的数据
def search_kx_data_from_mysql(flag=0):
    result_dict = {}
    result_list = []

    # 直接搜索10条新闻
    result_list.extend(search_data_from_mysql(myModel=KX, n=MAX_NEWS_NUMBER, label=1))
    # 就这十条数据，还是按照领导人数据排个序吧
    kx_leaders_list = get_kx_leaders_from_mysql()
    # flag = 0 推送三条，flag  =1 时，就是点击更多，就加载10条新闻
    if not flag:
        temp_list = sort_kx_news(news_list=result_list, keywords_list=kx_leaders_list)[:3]
    else:
        temp_list = sort_kx_news(news_list=result_list, keywords_list=kx_leaders_list)
    # 要闻，要闻这里是按照优先级排序的
    result_dict['news'] = temp_list

    #  通知，flag = 0 三条 flag = 1 10条
    if not flag:
        temp_list = search_data_from_mysql(myModel=KX, n=LIMIT_NEWS, label=3)
    else:
        temp_list = search_data_from_mysql(myModel=KX, n=MAX_NEWS_NUMBER, label=3)
    result_dict['notices'] = temp_list
    # 视频  flag = 0 三条 flag = 1 10条
    if not flag:
        temp_list = search_data_from_mysql(myModel=KX, n=LIMIT_NEWS, label=4)
    else:
        temp_list = search_data_from_mysql(myModel=KX, n=MAX_NEWS_NUMBER, label=4)
    result_dict['video'] = temp_list
    # 按照时间检索找五张img字段不为空的数据,用于轮播图

    result_dict['banners'] = search_data_from_mysql(myModel=KX, n=LIMIT_NEWS, LB=True)
    return result_dict


# 补充到足够数量的新闻+
def get_enough_news(news_list, mymodels):
    num_news = len(news_list)
    if num_news >= MAX_NEWS_NUMBER:
        return
    # 现获取到信息的id
    id_list = []
    for one_news in news_list:
        news_id = one_news['news_id']
        index = news_id.rindex("_")
        number = news_id[index + 1:]
        id_list.append(int(number))
    news_list.extend(search_data_from_mysql(mymodels, 50, id__list=id_list))


# 刚开始过滤掉一周以前的新闻
def diff_time(news_list):
    result_list = []
    for one_news in news_list:
        news_time = one_news['news_time']
        try:
            diff = datetime.today().date() - datetime.strptime(news_time, '%Y-%m-%d').date()
            if diff.days < WEEK:
                result_list.append(one_news)
        except Exception as err:
            print(err)
    return result_list


# 按照规则排序
def sort_all_news(news_list, branch=None, channel=None, keywords_list=[]):
    return []


# 获取所有的频道
def get_all_channel():
    result_list = []
    temp_list = ChannelToDatabase.objects.values_list('channel')
    for one in temp_list:
        result_list.append(one[0])
    return result_list


# 按照条件数据，返回一个列表
def search_data_from_mysql(myModel, n=MAX_NEWS_NUMBER, source=None, id__list=[], label=None, LB=False, ):
    result = []
    data = None
    ### id__list 和 source__list是默认状态
    if label and source and (not LB):  # label 和source 无图 地方科协1.3
        try:
            data = myModel.objects.filter(hidden=1).exclude(id__in=id__list).filter(source=source).filter(label=label).values_list('id',
                                             'title',
                                             'img',
                                             'time',
                                             'source',
                                             'comment',
                                             'like',
                                             'priority',
                                             'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))

    elif label and source and LB:  # 带label source 还有图 地方科协2
        try:
            data = myModel.objects.filter(hidden=1).exclude(id__in=id__list).filter(source=source).filter(label=label).filter(~Q(img=None)).filter(
                ~Q(img='')).filter(~Q(img=' ')).values_list('id', 'title', 'img', 'time',
                                                            'source', 'comment', 'like',
                                                            'priority', 'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))
    elif source and LB:# 只有source和图 地方科协轮播图
        try:
            data = myModel.objects.filter(hidden=1).exclude(id__in=id__list).filter(source=source).filter(~Q(img=None)).filter(
                ~Q(img='')).filter(~Q(img=' ')).values_list('id', 'title', 'img', 'time',
                                                            'source', 'comment', 'like',
                                                            'priority', 'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))

    elif source:#只有source 就可以查到 全国学会
        try:
            data = myModel.objects.filter(hidden=1).filter(source=source).exclude(id__in=id__list).values_list('id',
                                                                                                             'title',
                                                                                                             'img',
                                                                                                             'time',
                                                                                                             'source',
                                                                                                             'comment',
                                                                                                             'like',
                                                                                                             'priority',
                                                                                                             'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))
    elif LB and label: #只有图和标签，无source 地方科协2（非主）
        try:
            data = myModel.objects.filter(hidden=1).exclude(id__in=id__list).filter(label=label).filter(~Q(img=None)).filter(
                ~Q(img='')).filter(~Q(img=' ')).values_list('id', 'title', 'img', 'time',
                                                            'source', 'comment', 'like',
                                                            'priority', 'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))
    elif label:#只有label就可以获取到
        try:
            data = myModel.objects.filter(hidden=1).filter(label=label).exclude(id__in=id__list).values_list('id',
                                                                                                             'title',
                                                                                                             'img',
                                                                                                             'time',
                                                                                                             'source',
                                                                                                             'comment',
                                                                                                             'like',
                                                                                                             'priority',
                                                                                                             'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))
    elif LB:#只想找有图的
        try:
            data = myModel.objects.filter(hidden=1).exclude(id__in=id__list).filter(~Q(img=None)).filter(~Q(img='')).filter(
                ~Q(img=' ')).values_list('id', 'title', 'img', 'time',
                                         'source', 'comment', 'like',
                                         'priority', 'label').order_by(
                '-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))
    else:#就找数据，无条件
        try:
            data = myModel.objects.filter(hidden=1).values_list(
                'id', 'title', 'img','time', 'source', 'comment', 'like', 'priority', 'label').order_by('-time')[:n]
        except Exception as err:
            print("{0}数据库检索不到数据".format(myModel._meta.db_table))


    if data:
        for one in data:
            temp_dict = {}
            news_id = str(myModel._meta.db_table) + '_' + str(one[0])
            temp_dict['news_id'] = news_id
            temp_dict['news_title'] = one[1]

            #在这里要进行img
            temp_dict['news_img'] = CommonMethod.get_correct_img(one[2])
            # temp_dict['news_img'] = '/' + str(one[2])
            temp_dict['news_time'] = str(one[3])
            # 新闻来源要特殊处理一下，展示给用户的是新闻简称
            temp_dict['news_source'] = CommonMethod.get_short_source(myModel, one[4])
            temp_dict['comment'] = one[5]
            temp_dict['like'] = one[6]
            temp_dict['priority'] = one[7]
            temp_dict['label'] = one[8]
            result.append(temp_dict)
    return result


####################################获取的中央领导人接口##################################################
#修改为获取run.log文件的数据
def get_china_top_news(request):
    result_dict = {}
    dateDict = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun',
                '07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
    with open(RUNPATH, encoding='UTF-8') as f:
        contents = f.read()
        # 当前日期
        Toady = datetime.now().date()
        fisrtIndex = 0
        for index in range(7):
            date_2 = Toady + timedelta(days=-index)
            year = str(date_2.year)
            month = str(date_2.month) if date_2.month > 9 else '0' + str(date_2.month)
            month = dateDict[month]
            day = str(date_2.day) if date_2.day > 9 else '0' + str(date_2.day)
            textTime = day + '/' + month + '/' + year
            #print(textTime)
            textTimeCounts = contents.count(textTime)
            result_dict[str(date_2)] = textTimeCounts
            #if textTimeCounts > 0 :
            fisrtIndex = contents.find(textTime) if textTimeCounts > 0 else fisrtIndex

            # if 'GET' in content:
            #     ret = re.compile(r'[(\d+)/(\w+)/(\d+)].*"GET')

        contents = contents[fisrtIndex:]

        allAgency = AgencyJg.objects.values_list()
        temp_dict ={}
        for one in allAgency:
            department = one[2]
            departmentNumber = one[1]
            departmentCounts = contents.count(departmentNumber)
            if departmentCounts > 0:
                temp_dict[department] = departmentCounts
        for one in sorted(temp_dict.items(), key=lambda item:item[1], reverse=True):
            result_dict[one[0]] = one[1]


    # try:
    #     chinaTopNews = ChinaTopNews.objects.all().order_by('-time')[0]
    #     result_dict['news_title'] = chinaTopNews.title
    #     result_dict['news_time'] = str(chinaTopNews.time)
    #     result_dict['news_img'] = CommonMethod.get_correct_img(chinaTopNews.img)
    #     result_dict['news_source'] = chinaTopNews.source
    #     result_dict['news_id'] = str(ChinaTopNews._meta.db_table) + '_' + str(chinaTopNews.id)
    # except Exception as err:
    #     print('读取置顶中央新闻失败')
    #     print(err)
    return HttpResponse(json.dumps(result_dict, ensure_ascii=False))


####################################新闻id返回新闻 内容，并记录用户画像###########################################
# 根据新闻id返回内容,并记录用户画像
def news_content(request):
    #没有新闻id直接返回
    try:
        news_id = request.GET.get('news_id')
    except:
        return HttpResponse(json.dumps([], ensure_ascii=False))
    try:
        user_id = request.GET.get('user_id')
    except Exception as err:
        user_id = None

        #print(err)
    # 根据新闻id获取到新闻的详情
    news_info_dict = accord_news_id_get_content_list(news_id)
    if not news_info_dict:
        return HttpResponse(json.dumps({}, ensure_ascii=False))
    # 找到user_id才进行用户画像
    try:
        if user_id:
            db_table, number = CommonMethod.get_table_and_id(news_id)
            # 只有科技热点和时政新闻记录用户画像
            if db_table == News._meta.db_table or db_table == TECH._meta.db_table:
                # 根据db_table获取到频道
                cur_channel = ChannelToDatabase.objects.filter(database=db_table).values_list('channel')[0][0]
                keyword_list = news_info_dict['keywords_list'].split(' ')
            else:
                cur_channel = None
                keyword_list = []
            record_user_image(user_id, cur_channel, keyword_list)
    except Exception as err:
        print('用户：{0}画像失败'.format(user_id))
        print(err)
    finally:
        news_info_dict.pop("keywords_list")
        return HttpResponse(json.dumps(news_info_dict, ensure_ascii=False))


# 根据新闻id,获取当前新闻的信息
def accord_news_id_get_content_list(news_id):
    db_table, number = CommonMethod.get_table_and_id(news_id)
    if not db_table:
        return {}
    # 根据db_table获取到models
    mymodels = CommonMethod.table_to_models(db_table)
    # 查到数据
    contents = mymodels.objects.filter(id=number).values_list('content', 'like', 'comment', 'keywords', 'title', 'time',
                                                              'source')
    # 保存结果
    result_dict = {}
    for one in contents:
        result_dict['news_content'] = one[0]
        result_dict['like'] = one[1]
        result_dict['comment'] = one[2]
        result_dict['keywords_list'] = one[3]
        result_dict['news_title'] = one[4]
        result_dict['news_time'] = str(one[5])
        result_dict['news_source'] = one[6]

    return result_dict


# 记录用户画像
def record_user_image(user_id, cur_channel, keywords_list):
    # 根据id搜索到用户
    if not keywords_list:
        return
    user = search_user_from_momgodb(id=user_id)
    if user:
        # 更新用户的画像
        update_uesr_iamges_accord_keywords_channel(user, cur_channel, keywords_list)


####################################新闻id返回相似新闻的列表####################################
# 返回相似的新闻列表
def similar_news_list(request):
    news_id = request.GET.get("news_id")
    if news_id:
        data = similar_news(news_id)
        return HttpResponse(json.dumps(data, ensure_ascii=False))
    else:
        return HttpResponse('news_id错误')


####################################以下都是爬虫更新入库函数####################################
#############################科协一家资讯入库###########
def update_kxyj_data():
    # 资讯
    try:
        news_list = spider.get_kxyj_news()
    except Exception as err:
        #print('科协一家新闻资讯')
        news_list = []
        #print(err)
    # 专家观点
    try:
        news_list.extend(spider.get_kxyj_exp_opi())
    except Exception as err:
        pass
        # print('专家观点出错')
        # print(err)

    if news_list:
        for one_news in news_list:
            news = TECH(**one_news)
            try:
                news.save()
                #print('Successful')
            except Exception as err:
                # print(err)
                pass


#######################置顶的时政新闻入库###################
def update_china_top_news():
    # 置顶的时政新闻
    try:
        data = spider.china_top_news()
        china_top_news = ChinaTopNews(**data)
    except Exception as err:
        #print('获取置顶的时政新闻失败')
        china_top_news = None
        #print(err)
    # 置顶时政新闻入库
    if china_top_news:
        try:
            china_top_news.save()
            #print('Successful')
        except Exception as err:
            pass
            # print('插入置顶的时政新闻失败')
            # print(err)


####################################科协官网数据入库###################
def update_kexie_news_into_mysql():
    try:
        news_list = spider.update_kexie_news()
    except Exception as err:
        #print('selenium获取科协官网失败')
        #print(err)
        try:
            news_list = spider.get_kexie_news_data_list()
        except Exception as err:
            pass
            #print('bs4获取科协官网失败')
            news_list = []
            #print(err)
    if news_list:
        for one_news in news_list:
            kx = KX(**one_news)
            try:
                kx.save()
                #print('Successful')
            except Exception as e:
                pass
                #print(e)
    # return HttpResponse('成功')


####################################人民网时政数据更新入库函数###################
def updata_get_rmw_news_data():
    try:
        news_list = spider.get_rmw_news_data()
    except Exception as err:
        #print('人民网时政数据错误')
        news_list = None
        #print(err)
    if news_list:
        for one_news in news_list:
            news = News(**one_news)
            try:
                news.save()
                #print('Successful')
            except Exception as e:
                pass
                #print(e)
    # return HttpResponse('人民网时政新闻入库成功')
    # return render(request,'news.html',{'news_list':news_list})


####################################人民网科技数据更新入库函数###################
def update_get_rmw_kj_data():
    try:
        news_list = spider.get_rmw_kj_data()
    except Exception as err:
        #print('人民网科技数据错误')
        news_list = None
        #print(err)
    if news_list:
        for one_news in news_list:
            news = TECH(**one_news)
            try:
                news.save()
                #print('Successful')
            except Exception as e:
                pass
                #print(e)
    # return HttpResponse('人民网科技数据入库成功')


####################################清洗科协的cast数据库中的科技热点和时政要闻入库###########################
def hanle_cast_into_mysql():
    try:
        handle_cast.start()
    except Exception as err:
        #pass
        print('清洗cast数据库入库出错')
        #print(err)
    # try:
    #     handle_cast.sz_kj()
    # except Exception as e:
    #     print("时政和科技热点数据入库出错")
    #     print(e)


####################################初始化相关函数###########################################

############初始化科协机关、事业单位、地方科协和全国学会的组织结构代码和名称###############
def save_org_into_mysql(request):
    try:
        initData.handle_organization()
    except Exception as e:
        return HttpResponse('初始化科协机构成功:{0}'.format(e))
    return HttpResponse('初始化科协机构成功')


# save_kexie_leader给mongodb插入一个样例
def save_leader(request):
    try:
        for name in kexie_leader.keys():
            kxLeader = KxLeaders(name=name)
            try:
                kxLeader.save()
            except Exception as e:
                print(e)
    except Exception as err:
        print('初始化科协领导')
        print(err)
    return HttpResponse('初始化科协领导成功')
