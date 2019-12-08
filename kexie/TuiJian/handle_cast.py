import jieba
import jieba.analyse
import pymysql
import datetime
import time
import re
from .define import *
from .spider import  *
from .models import *
from .organiza import *

#时政新闻
def sz_kj():
    db_table = 'kexie'
    host = "192.168.171.48"
    db,cursor = link_db(db_table,host)
    table = 'media'
    data= ['人民网-时政频道','人民网-国际频道','人民网-中国共产党新闻网']
    result_list = []
    for one in data:
        #print(one)
        sql = "select * from {0} where source ='{1}'order by time  desc  limit 1000".format(table, one)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title,url,content,img,news_time,author,keywords,source = one_news[1], one_news[2], one_news[3], one_news[4], one_news[5], one_news[6], one_news[7], one_news[8]
                # 数据封装进字典
                result_list.append(package_data_dict(title, url, content, news_time, source))
        except:
            pass
            #print('出现错误')
        save_data_to_mysql(result_list, News)

    ###科技
    data= ['人民网-科技频道','人民网-国际频道','人民网-IT频道','中国科技网']
    result_list = []
    for one in data:
        #print(one)
        sql = "select * from {0} where source like '{1}%'order by time  desc  limit 1000".format(table, one)
        #print(sql)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title,url,content,img,news_time,author,keywords,source = one_news[1], one_news[2], one_news[3], one_news[4], one_news[5], one_news[6], one_news[7], one_news[8]
                # 数据封装进字典
                result_list.append(package_data_dict(title, url, content, news_time, source))
        except:
            pass
            #print('出现错误')
        save_data_to_mysql(result_list, TECH)
    close(db,cursor)


#处理数据库
def start():
    #
    try:
        db_table = 'cast'
        host = "192.168.171.48"
        cast_db,cast_cursor = link_db(db_table,host)
    # print('开始处理media_content数据库的新闻')
    # #处理主流媒体
    # cast_table='media_content'
    #
    # #处理科协
    # media= ["人民网-","央视网","中国日报网","中国经济网","中国青年网","光明网","澎湃新闻","中国科学院",
    #      "中国科技网","中国新闻网","国际在线","央广网","北京时间",
    #      "中央电视台","新华网"]
    # data = handle_media_content_list(media,cast_table,cast_cursor)
    #
    # #保存数据到数据库
    # save_data_to_mysql(data,TECH)
    #print('开始处理website数据库的新闻')
    # 处理website
        cast_table = 'website'
        data = handle_website_xuehui(xuehui(), cast_table, cast_cursor)
    # 保存数据到数据库
        save_data_to_mysql(data,QGXH)

    #在处理地方科协的数据
        # data = handle_website_shenghui(shenghui(),cast_table,cast_cursor)
        # save_data_to_mysql(data,DFKX)

    # #处理科协
    # media = ["创新战略研究院", "中国科普研究所", "农村专业技术服务中心", "青少年科技中心", "企业创新服务中心"]
    # data = handle_website_list(media,cast_table,cast_cursor)
    # save_data_to_mysql(data, KX)

    #print('开始处理wechat数据库的新闻')
    #处理wechat
    # 全国学会
        cast_table = 'wechat'

    # 先处理学会的数据
        data = handle_wechat_xuehui(xuehui(), cast_table, cast_cursor)
        save_data_to_mysql(data, QGXH)

    # 在处理地方科协的数据
    #     data = handle_wechat_shenghui(shenghui(), cast_table, cast_cursor)
    #     save_data_to_mysql(data,DFKX)

    # # 处理科协
    # kx = [
    #       "科协改革进行时", "创新研究", "中国绿发会", "企业创新最前沿",
    #       "中国科协青少年科技中心", "今日科协", "学会服务365",
    #       "青少年高校科学营", "创响中国",
    #       "港澳台大学生暑期实习活动", ]
    # data = handle_wechat_list(kx, cast_table, cast_cursor)
    # save_data_to_mysql(data, KX)

    # # 处理科普
    # kp = ['掌上科技馆', '蝌蚪五线谱', '科学媒介中心', '数学英才', '气象e新', '知识产权杂志']
    # data = handle_wechat_list(kp, cast_table, cast_cursor)
    # save_data_to_mysql()
    #
    # # 处理党建
    # dj = ['科技社团党建']
    # data = handle_wechat_list(dj, cast_table, cast_cursor)
    # save_data_to_mysql()

    #增加一点时政新闻
    #sz_kj()
    except:
        pass
    finally:
        close(cast_db, cast_cursor)


def save_data_to_mysql(data,myModel):
    for one_data in data:
        #print(one_data)
        news = myModel(**one_data)
        try:
            news.save()
        except Exception as e:
            pass
            #print(e)


####################################处理media_content##############################
#data参数是一个列表
def handle_media_content_list(data, table,cursor):
    result_list=[]
    for one in data :
        #print(one)
        sql = "select * from {0} where 来源 like '{1}%'order by 日期 desc  limit 1000".format(table,one)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date, source = one_news[1], one_news[5], one_news[4], one_news[3], one_news[2]
                # 没有content就不要了
                if not content or content == "空":
                    continue
                #处理日期
                if date != '空':
                    date = date.split(' ')[0]
                else:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=source))

        except :
            pass
            #print('出现错误')
    return result_list

########################处理website#############################
#处理全国学会的数据
def handle_website_xuehui( data, table,cursor):
    result_list=[]
    for one in data :
        #print(one)
        sql = "select * from {0} where 来源 like'{1}'order by 日期 desc limit 100 ".format(table,one)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date, source = one_news[5], one_news[7], one_news[10], one_news[3], one_news[0]
                # 没有content就不要了
                if not content or content == "空"  or title == "空" or source == "空":
                    continue
                #处理日期
                date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=source,tag = 2))

        except :
            pass
            #print('出现错误')
    #print(result_list)
    return result_list

#处理地方科协的
def handle_website_shenghui( data, table,cursor):
    result_list=[]
    for one in data :
        #print(one)
        all_dfkx=dfkx()
        for one_dfkx in all_dfkx:
            if one in one_dfkx:
                quan_source = one_dfkx
                break
        sql = "select * from {0} where 来源 like '{1}%'order by 日期 desc limit 100 ".format(table,one)
        #对后边的source要做一个处理
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date, source = one_news[5], one_news[7], one_news[10], one_news[3], one_news[0]

                # 没有content就不要了
                if not content or content == "空"  or title == "空" or source == "空":
                    continue
                #处理日期
                if date != '空':
                    date = date.split(' ')[0]
                else:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=quan_source,tag = 1))

        except Exception as err:
            pass
            # print(err)
            # print('出现错误')
    #print(result_list)
    return result_list

#处理参数是一个列表
def handle_website_list(data, table,cursor):
    result_list=[]
    result_dict = {}
    for one in data :
        #print(one)
        sql = "select * from {0} where 来源 like '{1}'order by 日期 desc  limit 100".format(table,one)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date, source = one_news[5], one_news[7], one_news[10], one_news[3], one_news[0]
                # 没有content就不要了
                if not content or content == "空":
                    continue
                #处理日期
                if date != '空':
                    date = date.split(' ')[0]
                else:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=source))

        except :
            pass
            #print('出现错误')
    return result_list

#################################处理wechat########################################

#处理全国学会的数据
def handle_wechat_xuehui( data, table,cursor):
    result_list=[]
    result_dict = {}
    for one in data :
        #print(one)
        sql = "select * from {0} where 来源 like'{1}%'order by 日期 desc limit 1000 ".format(table,one)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date, source = one_news[1], one_news[2], one_news[5], one_news[3], one_news[4]
                # 没有content就不要了
                if not content or content == "空":
                    continue
                #处理日期
                if date != '空':
                    date = date.split(' ')[0]
                else:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=source,tag =2))

        except :
            pass
            #print('出现错误')
    return result_list

#处理地方科协的
def handle_wechat_shenghui( data, table,cursor):
    result_list=[]
    result_dict = {}
    for one in data :
        #print(one)
        all_dfkx=dfkx()
        for one_dfkx in all_dfkx:
            if one in one_dfkx:
                quan_source = one_dfkx
                break
        sql = "select * from {0} where 来源 like '{1}%'order by 日期 desc limit 100 ".format(table,one)
        #对后边的source要做一个处理
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date = one_news[1], one_news[2], one_news[5], one_news[3]

                # 没有content就不要了
                if not content or content == "空":
                    continue
                #处理日期
                if date != '空':
                    date = date.split(' ')[0]
                else:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=quan_source,tag =1))

        except :
            pass
            #print('出现错误')
    return result_list

#处理参数是一个列表
def handle_wechat_list(data, table,cursor):
    result_list=[]
    for one in data :
        #print(one)
        sql = "select * from {0} where 来源='{1}'order by 日期 desc limit 100 ".format(table,one)
        try:
            cursor.execute(sql)
            all_news = cursor.fetchall()
            for one_news in all_news:
                title, link, content, date, source = one_news[1], one_news[2], one_news[5], one_news[3], one_news[4]
                # 没有content就不要了
                if not content or content == "空":
                    continue
                #处理日期
                if date != '空':
                    date = date.split(' ')[0]
                else:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')
                #数据封装进字典
                result_list.append(package_data_dict(title=title, url=link, content=content,date=date, source=source))

        except :
            pass
            #print('出现错误')
    return result_list
#tag = 1 代表的是地方科协，tag =2 代表的是全国学会
def package_data_dict(title=None, url=None, img =None,content=None, date=None, source=None,tag = None):
    temp_dict = {}
    keywords = TF_IDF(content,MAX_KEYWORDS)
    if len(keywords) > 4:
        temp_dict['title'] = title
        temp_dict['url'] = url
        temp_dict['content'] = content
        temp_dict['img'] = img
        temp_dict['time'] = date
        temp_dict['author'] = ''
        temp_dict['keywords'] = ' '.join(keywords)
        if tag == 1:
            try:
                source = AgencyDfkx.objects.filter(department=source)[0]
            except Exception as err:
                #print(err)
                source = None
                #print('地方科协来源错误')
        if tag == 2:
            try:
                source = AgencyQgxh.objects.filter(department=source)[0]
            except Exception as err:
                #print(err)
                source = None
                #print('全国学会来源错误')
        temp_dict['source'] = source
    return temp_dict



#链接数据库，192.168.171.48
def link_db (db_name,host):
    db = pymysql.connect(host=host,user='root', password='password', port=3306,db = db_name)
    cursor = db.cursor()
    return db,cursor

def close(db,cursor):
    try:
        cursor.close()
        db.close()
    except Exception as err:
        pass
        #print(err)

