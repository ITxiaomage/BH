from .models import *


# 拿到source
def get_short_source(myModel, source):
    if myModel == QGXH:
        try:
            temp_source = AgencyQgxh.objects.filter(hidden=1).filter(department=source).values_list('short')[0][0]
        except:
            temp_source = source

    elif myModel == DFKX:
        try:
            temp_source = AgencyDfkx.objects.filter(hidden=1).filter(department=source).values_list('short')[0][0]
        except:
            temp_source = source
    else:
        temp_source = source
    if temp_source:
        return temp_source
    else:
        return source


# 根据db_table获取模型名字
def table_to_models(db_table):
    # 只能用这种方法了
    if News._meta.db_table == db_table:
        mymodels = News
    elif KX._meta.db_table == db_table:
        mymodels = KX
    elif DFKX._meta.db_table == db_table:
        mymodels = DFKX
    elif QGXH._meta.db_table == db_table:
        mymodels = QGXH
    elif TECH._meta.db_table == db_table:
        mymodels = TECH
    elif ChinaTopNews._meta.db_table == db_table:
        mymodels = ChinaTopNews
    return mymodels
# 根据新闻id获取到数据表和在表中的id
def get_table_and_id(news_id):
    try:
        index = news_id.rindex('_')
        db_table = news_id[:index]
        number = int(news_id[index + 1:])
    except:
        return None, None
    return db_table, number