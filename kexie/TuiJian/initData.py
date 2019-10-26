from . import models
import xlrd
import pandas as pd
from .define import *

#初始化机构组织
def handle_organization():
    # 保存结果的字典

    result_dict = {}
    # 机关
    df = pd.read_excel(jiggou_path, sheet_name='机关')  # 可以通过sheet_name来指定读取的表单
    data = df.ix[:, ['id', '名称']].values  # id，名称
    for one in data:
        result_dict[str(one[0])] = one[-1]


    # 直属事业单位
    df = pd.read_excel(jiggou_path, sheet_name='直属事业单位')  # 可以通过sheet_name来指定读取的表单
    data = df.ix[:, ['id', '名称']].values  # id，名称
    for one in data:
        result_dict[str(one[0])] = one[-1]

    for id,name in result_dict.items():
        org_data = models.AgencyJg(number=id,department=name)
        org_data.save()


    result_dict = {}
    # 地方科协
    df = pd.read_excel(jiggou_path, sheet_name='地方科协')  # 可以通过sheet_name来指定读取的表单
    data = df.ix[:, ['id', '名称']].values  # id，名称
    for one in data:
        result_dict[str(one[0])] = one[-1]
    for id,name in result_dict.items():
        org_data = models.AgencyDfkx(number=id,department=name)
        org_data.save()

    result_dict = {}
    # 全国学会
    df = pd.read_excel(jiggou_path, sheet_name='全国学会')  # 可以通过sheet_name来指定读取的表单
    data = df.ix[:, ['id', '名称']].values  # id，名称
    for one in data:
        result_dict[str(one[0])] = one[-1]
    for id,name in result_dict.items():
        org_data = models.AgencyQgxh(number=id,department=name.split(' ')[-1],index=name.split(' ')[0])
        org_data.save()
