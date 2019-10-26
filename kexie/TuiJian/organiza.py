from .models import *

#根据编号获取到部门名称
def accord_number_get_department(number):
    result = get_number_to_department(number)
    if  result:
        return result[0]
    else:
        return ''

#获取地方科协
def dfkx():
    return get_department(AgencyDfkx)

#获取全国学会
def xuehui():
    return get_department(AgencyQgxh)

#获取科协机关单位
def kxjg():
    return get_department(AgencyJg)

#地方科协编号
def num_dfkx():
    return get_number(AgencyDfkx)

#全国学会编号
def num_xuehui():
    return get_number(AgencyQgxh)

#获取科协机关单位编号
def num_kxjg():
    return get_number(AgencyJg)

def get_number_to_department(number):
    result_list = []
    temp_list = []
    if number in num_dfkx():
        temp_list = AgencyDfkx.objects.filter(number=number).values_list('department')
    elif number in num_xuehui():
        temp_list = AgencyQgxh.objects.filter(number=number).values_list('department')
    elif number in num_kxjg():
        temp_list = AgencyJg.objects.filter(number=number).values_list('department')
    for one_data in temp_list:
        result_list.append(one_data[0])
    return result_list

#得到单位的编号
def get_number(myModels):
    result_list = []
    templist = myModels.objects.all().values_list('number')
    for one_data in templist:
        result_list.append(one_data[0])
    return result_list

#得到部门名称
def get_department(myModels):
    result_list = []
    templist = myModels.objects.all().values_list('department')
    for one_data in templist:
        result_list.append(one_data[0])
    return result_list

def shenghui ():
    shenghui = ["北京",
        "天津",
        "河北",
        "山西",
        "内蒙",
        "辽宁",
        "吉林",
        "黑龙",
        "上海",
        "江苏",
        "浙江",
        "安徽",
        "福建",
        "江西",
        "山东",
        "河南",
        "湖北",
        "湖南",
        "广东",
        "广西",
        "海南",
        "重庆",
        "四川",
        "贵州",
        "云南",
        "西藏",
        "陕西",
        "甘肃",
        "青海",
        "宁夏",
        "新疆生产建设兵团",
        "新疆"
    ]
    return shenghui