
#默认的中央领导人照片
IMG = 'http://www.gov.cn/xinwen/site1/20140905/18037327d8e41573fa3901.jpg'

#训练好的词向量模型路径
#w2v_path_model ='E:\推荐相关\model/w2v.model'
w2v_path_model ='/home/BH_TuiJian/kexie/w2v.model'
#存放科协机构的文件路径
#jiggou_path = r'E:\推荐相关\机构.xls'
jiggou_path = r'/home/BH_TuiJian/kexie/机构.xls'

#每篇文章提取的关键字最大数，用户设置用户画像
MAX_KEYWORDS = 10
#中国科协每个新闻的限制数量
LIMIT_NEWS = 3
#提取的新闻的最大数量
MAX_NEWS_NUMBER = 10
#去数据库检索数据的最大值
MAX_SEARCH_NEWS= 500
#定义一周的时间
WEEK= 7

#模型名字和数据库的设计
models_to_db_table = {"news":"News","kx":"KX","dfkx":"DFKX","qgxh":"QGXH","tech":"TECH","chinaTopNews":"ChinaTopNews"}
#数据库表和频道的映射
table_to_channel = {"时政要闻":"news", "中国科协":"kx","地方科协":"dfkx","全国学会":"qgxh","科技热点":"tech"}
#定义全国学会频道
CHANNEL_QGXH='全国学会'
#定义地方科协频道
CHANNEL_DFKX='地方科协'

#定义时政要闻频道
CHANNEL_SZYW='时政要闻'
#定义科技热点
CHANNEL_KJRD='科技热点'
#定义中国科协
CHANNEL_ZGKX='中国科协'


#定义办公厅ID
BGT= '2000000309'

#定义mongodb的数据库
MONGODB_DB = 'kexie'
#定义mongodb上的用户画像collection
USER_IMAGE = 'user_image'
#定义机构画像
ORG_IMAMGE= 'org_image'

#定义用户画像中相似度的值
SIMILIAR = 0.9
#相似性最低值
MIN_SIMILIAR = 0.2
#用户画像分数初始值
INIT_SCORE = 50

#汉明距离值
SIMHASH_DISTINCT = 10
kexie_leader = {
            "万钢":100,
            "怀进鹏":100,
            "徐延豪":100,
            "孟庆海":100,
            "束为":100,
            "宋军":100,
            "王守东":100,
            "殷皓":100,
            "马伟明":100,
            "王曦":100,
            "邓秀新":100,
            "李华":100,
            "李洪":100,
            "李静海":100,
            "何华武":100,
            "沈岩":100,
            "陈左宁":100,
            "周守为":100,
            "郑晓静":100,
            "赵玉沛":100,
            "施一公":100,
            "袁亚湘":100,
            "高松":100,
            "潘建伟":100
        }



