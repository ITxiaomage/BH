from django.db import models
#最大最小值验证器
from django.core.validators import MaxValueValidator,MinValueValidator
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class NewsBase(models.Model):
    title = models.CharField(max_length=255,null=False,unique=True,verbose_name='标题')
    url = models.CharField(max_length=255,null=True,verbose_name='新闻链接',blank=True)
    img =  models.ImageField(max_length=255,null=True,verbose_name='新闻图片',blank=True,upload_to='mgh')
    content = RichTextUploadingField(null=False,verbose_name='新闻内容')
    author = models.CharField(max_length=255,null=True,verbose_name='作者',blank=True)
    keywords = models.CharField(max_length=255,null=True,verbose_name='关键字',blank=True)
    time = models.CharField(max_length=255,null=True,verbose_name='发布时间',blank=True)
    source = models.CharField(max_length=255,null=True,verbose_name='新闻来源',blank=True)
    #标签，科协下分的：智库、学术、科普、党建。还有单独表明的ring
    label = models.CharField(max_length=255,null=True,verbose_name='新闻标签',blank=True)
    comment = models.IntegerField(default= 0,verbose_name='评论数',blank=True)
    like = models.IntegerField(default=0,verbose_name='点赞',blank=True)
    #限制人工干预优先级的最大值是10，最小值是0
    priority =  models.IntegerField(default= 0,validators=[MaxValueValidator(10),MinValueValidator(0)],verbose_name='优先级',blank=True)
    #屏蔽新闻的标志,默认不屏蔽设置为1，屏蔽就设置为0
    hidden = models.BooleanField(default= True,verbose_name='是否推送',blank=True)
    #今天推送的新闻的排序，值越大，新闻的优先级越高
    today = models.IntegerField(default= 0,validators=[MaxValueValidator(100),MinValueValidator(0)],blank=True)

    def __str__(self):
        return self.title

    class Meta:
        managed =True
        abstract = True
        ordering=['-time']

class News(NewsBase):
    class Meta:
        db_table = "news"
        verbose_name = "时政要闻"
        verbose_name_plural = "时政要闻"

class KX(NewsBase):
    class Meta:
        db_table = "kx"
        verbose_name = "中国科协新闻"
        verbose_name_plural = "中国科协新闻"

class DFKX(NewsBase):
    class Meta:
        db_table = "dfkx"
        verbose_name = "地方科协新闻"
        verbose_name_plural = "地方科协新闻"

class QGXH(NewsBase):
    class Meta:
        db_table = "qgxh"
        verbose_name = "全国学会新闻"
        verbose_name_plural = "全国学会新闻"
class TECH(NewsBase):
    class Meta:
        db_table = "tech"
        verbose_name = "科技热点新闻"
        verbose_name_plural = "科技热点新闻"

class ChinaTopNews(NewsBase):
    class Meta:
        db_table = "chinaTopNews"
        verbose_name = "中央领导人新闻"
        verbose_name_plural = "中央领导人新闻"

class AgencyBase(models.Model):
    number = models.CharField(max_length=255,null= False,unique=True,verbose_name='部门编号')
    department = models.CharField(max_length=255, null=False, unique=True,verbose_name='部门名称')
    index = models.CharField(max_length=255)
    #当前部门是否可用，可用为1，不可用为0
    hidden = models.BooleanField(default= True)
    class Meta:
        abstract = True


class AgencyJg(AgencyBase):
    class Meta:
        db_table = 'agency_jg'
        verbose_name = "科协机关及事业单位"
        verbose_name_plural = "科协机关及事业单位"

class AgencyDfkx(AgencyBase):
    class Meta:
        db_table = 'agency_dfkx'
        verbose_name = "地方科协组织"
        verbose_name_plural = "地方科协组织"


class AgencyQgxh(AgencyBase):
    class Meta:
        db_table = 'agency_qgxh'
        verbose_name = "全国学会组织"
        verbose_name_plural = "全国学会组织"


class ChannelToDatabase(models.Model):
    channel = models.CharField(max_length=255,unique=True,null=False)
    database =  models.CharField(max_length=255,unique=True,null=False)
    class Meta:
        db_table = 'channelToDatabase'
        verbose_name = "频道和数据库的映射"
        verbose_name_plural = "频道和数据库的映射"

class KxLeaders(models.Model):
    name = models.CharField(max_length=255,null=False,verbose_name='名字')
    #可见
    hidden = models.BooleanField(default=True, verbose_name='状态', blank=True)
    class Meta:
        db_table = 'leaders'
        verbose_name = "科协领导"
        verbose_name_plural = "科协领导"