from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
#最大最小值验证器
from django.core.validators import MaxValueValidator,MinValueValidator
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User, PermissionsMixin
#from DjangoUeditor.models import UEditorField

from xadmin.plugins.auth import User
# model.pys

class AgencyBase(models.Model):
    number = models.CharField(max_length=255,null= False,unique=True,verbose_name='部门编号')
    department = models.CharField(max_length=255, null=False, unique=True,verbose_name='部门名称')
    short = models.CharField(max_length=255,null=True,verbose_name='简称',default='')
    index = models.CharField(max_length=255)
    #当前部门是否可用，可用为1，不可用为0
    hidden = models.BooleanField(default= True,verbose_name='状态')
    def __str__(self):
        return self.department

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

class NewsBase(models.Model):
    title = models.CharField(max_length=255,null=False,unique=True,verbose_name='标题')
    url = models.CharField(max_length=255,null=True,verbose_name='新闻链接',blank=True)
    img =  models.ImageField(max_length=255,null=True,verbose_name='新闻图片',blank=True,upload_to='mgh')
    content = RichTextUploadingField(null=False,verbose_name='新闻内容')
    author = models.CharField(max_length=255,null=True,verbose_name='作者',blank=True)
    keywords = models.CharField(max_length=255,null=True,verbose_name='关键字',blank=True)
    time = models.DateField(null=True,verbose_name='发布时间',blank=True)
    #新闻标签，不同的标签代表内容见define.py
    mark = ((1, '上'),
             (2, '中'),
             (3, '下'),
            (4,'视频')
            )
    label = models.IntegerField(choices=mark, null=True,verbose_name='新闻标签',blank=True)
    comment = models.IntegerField(default= 0,verbose_name='评论数',blank=True)
    like = models.IntegerField(default=0,verbose_name='点赞',blank=True)
    #限制人工干预优先级的最大值是100，最小值是0
    priority =  models.IntegerField(default= 0,validators=[MaxValueValidator(100),MinValueValidator(0)],verbose_name='优先级',blank=True)
    #屏蔽新闻的标志,默认不屏蔽设置为1，屏蔽就设置为0
    hidden = models.BooleanField(default= False,verbose_name='是否推送',blank=True)

    def go_to(self):
        from django.utils.safestring import mark_safe
        if self.url:
            return mark_safe("<a href = '{0}' target=_bank >跳转</a>".format(self.url))
        return '无'

    go_to.short_description = '原始网页'

    def __str__(self):
        return self.title

    class Meta:
        managed =True
        abstract = True
        ordering=['-time']


## 临时增加一个疫情春节的表
class YQCJ(NewsBase):
    source = models.CharField(max_length=255, null=True, verbose_name='新闻来源', blank=True)
    class Meta:
        db_table = "yqcj"
        verbose_name = "疫情春节新闻"
        verbose_name_plural = "疫情春节新闻"




## 临时增加一个疫情防控的表
class YQFK(NewsBase):
    source = models.CharField(max_length=255, null=True, verbose_name='新闻来源', blank=True)
    class Meta:
        db_table = "yqfk"
        verbose_name = "疫情防控新闻"
        verbose_name_plural = "疫情防控新闻"


class News(NewsBase):
    source = models.CharField(max_length=255, null=True, verbose_name='新闻来源', blank=True)
    class Meta:
        db_table = "news"
        verbose_name = "时政要闻"
        verbose_name_plural = "时政要闻"

class KX(NewsBase):
    source = models.CharField(max_length=255, null=True, verbose_name='新闻来源', blank=True)
    class Meta:
        db_table = "kx"
        verbose_name = "中国科协新闻"
        verbose_name_plural = "中国科协新闻"

class DFKX(NewsBase):
    parent_link = True
    source = models.ForeignKey(AgencyDfkx,to_field="department",db_column='source',on_delete=models.CASCADE,verbose_name='新闻来源', blank=True,default='')
    class Meta:
        db_table = "dfkx"
        verbose_name = "地方科协新闻"
        verbose_name_plural = "地方科协新闻"

class QGXH(NewsBase):
    parent_link = True
    source = models.ForeignKey(AgencyQgxh, to_field="department",db_column='source',on_delete=models.CASCADE, verbose_name='新闻来源', blank=True,default='')
    class Meta:
        db_table = "qgxh"
        verbose_name = "全国学会新闻"
        verbose_name_plural = "全国学会新闻"
class TECH(NewsBase):
    source = models.CharField(max_length=255, null=True, verbose_name='新闻来源', blank=True)
    class Meta:
        db_table = "tech"
        verbose_name = "科技热点新闻"
        verbose_name_plural = "科技热点新闻"

class ChinaTopNews(NewsBase):
    source = models.CharField(max_length=255, null=True, verbose_name='新闻来源', blank=True)
    class Meta:
        db_table = "chinaTopNews"
        verbose_name = "中央领导人新闻"
        verbose_name_plural = "中央领导人新闻"


class ChannelToDatabase(models.Model):
    channel = models.CharField(max_length=255,unique=True,null=False)
    database = models.CharField(max_length=255,unique=True,null=False)
    class Meta:
        db_table = 'channelToDatabase'
        verbose_name = "频道和数据库的映射"
        verbose_name_plural = "频道和数据库的映射"

class KxLeaders(models.Model):
    name = models.CharField(max_length=255,null=False,verbose_name='名字')
    #可见
    hidden = models.BooleanField(default=True, verbose_name='状态', blank=True)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'leaders'
        verbose_name = "科协领导"
        verbose_name_plural = "科协领导"


class ControlQgxh(models.Model):
    user = models.OneToOneField(User, verbose_name='用户名',on_delete=models.CASCADE)
    is_admin = models.BooleanField('全部学会权限', default=False)
    source = models.ForeignKey(AgencyQgxh, to_field="department",db_column='source',on_delete=models.CASCADE, verbose_name='新闻来源', blank=True,default='')

    def __unicode__(self):
        return '%s' % self.user
    def __str__(self):
        return '用户{0}对于{1}的权限'.format(str(self.user),str(self.source))

    class Meta:
        verbose_name = '全国学会权限控制'
        verbose_name_plural = verbose_name

class ControlDfkx(models.Model):
    user = models.OneToOneField(User, verbose_name='用户名',on_delete=models.CASCADE)
    is_admin = models.BooleanField('全部地方科协权限', default=False)
    source = models.ForeignKey(AgencyDfkx, to_field="department",db_column='source',on_delete=models.CASCADE, verbose_name='新闻来源', blank=True,default='')

    def __unicode__(self):
        return '%s' % self.user
    def __str__(self):
        return '用户{0}对于{1}的权限'.format(str(self.user),str(self.source))
    class Meta:
        verbose_name = '地方科协权限控制'
        verbose_name_plural = verbose_name