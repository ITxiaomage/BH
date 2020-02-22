from django.contrib.auth import get_permission_codename
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as new_fliter
from django.contrib.admin import SimpleListFilter
from django.shortcuts import reverse, render
# 用户可以批量操作
from django.contrib import messages
from django import forms
from xadmin.layout import Main, Fieldset, Side

from .models import *
from .rules import *
from xadmin import views
import xadmin


class GlobalSetting(object):
    site_title = "中国科协新闻管理系统"

    site_footer = "中国科学技术协会"

    menu_style = "accordion"

xadmin.site.register(views.CommAdminView, GlobalSetting)


# 主题
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSetting)


class NewOrgBaseClass(object):
    # 显示的字段
    list_display = ['number', 'department', 'short', 'hidden']
    # 每页显示的数量
    list_per_page = 30
    list_display_links = ['number', 'department']
    # 操作选项
    actions_on_top = True
    # 搜索器
    search_fields = ['number', 'department']
    # 显示
    fields = ['number', 'department', 'short', 'hidden']
    # 排序
    ordering = ('id',)
    # 可编辑
    list_editable = ['short']
    readonly_fields = ("department", 'number')


class NewNewsBaseClass(object):
    list_filter = ['time', 'source']
    list_editable = ['priority', 'hidden', 'source']
    # 每页显示的数量
    list_per_page = 30

    # 显示缩略图
    def img_data(self, obj):
        if obj.img and hasattr(obj.img, 'url'):
            if 'http' in obj.img.url:
                return format_html('<img src="{0}" width="150px" height="150px"/>'.format(obj.img))
            else:
                return format_html('<img src="{0}" width="150px" height="150px"/>'.format(obj.img.url))
        else:
            return '无'

    img_data.short_description = '新闻图片'

    # 显示的字段
    list_display = ['title', 'img_data', 'go_to', 'time', 'source', 'priority', 'hidden']

    list_display_links = ['title', 'source', "time"]

    # 设置空值
    empty_value_display = '无'
    # 操作选项
    actions_on_top = True
    # 还原按钮，删除的信息可以还原
    reversion_enable = True
    # 搜索器
    search_fields = ['title', 'content']
    # 设置外键位搜索格式
    relfield_style = 'fk_ajax'
    # 跳转字段
    ordering = ('-time',)

    def del_imgs(self, request, queryset):
        queryset.update(img=None)
        messages.success(request, "删除图片成功")


    del_imgs.short_description = "删除图片"
    actions = [del_imgs]
    #内部排版
    form_layout = (
        Main(
            Fieldset('基本信息',
                     'title', 'img', 'priority', 'time', 'label', 'source', 'author', 'hidden'),
            Fieldset('新闻内容',
                     'content', ),
        ),
        Side(
            Fieldset('其它', 'url', 'comment', 'like','keywords'),
        )
    )
    readonly_fields = ('comment', 'like', 'keywords')
    #exclude = ['url']

class KXAdmin(NewNewsBaseClass):
    pass


xadmin.site.register(KX, KXAdmin)


class DFKXAdmin(NewNewsBaseClass):
    list_editable = ['priority', 'hidden']

    # 重写queryset()或者get_list_display()，list view的权限也做到了对象级隔离
    def queryset(self):
        qs = super(DFKXAdmin, self).queryset()
        if self.request.user.is_superuser or is_dfkx_admin(self.request.user):
            return qs
        try:
            return qs.filter(source=self.request.user.controldfkx.source)
        except AttributeError:
            return None

    # exclude = ('source',)
    # 设计预填充字段
    def save_models(self):
        try:
            self.new_obj.source = self.request.user.controldfkx.source
        except:
            pass
        finally:
            super(DFKXAdmin, self).save_models()


xadmin.site.register(DFKX, DFKXAdmin)


# 重写权限管理
class QGXHAdmin(NewNewsBaseClass):
    list_editable = ['priority', 'hidden']

    # exclude = ('source',)
    # 设计预填充字段
    def save_models(self):
        try:
            self.new_obj.source = self.request.user.controlqgxh.source
        except:
            pass
        finally:
            super(QGXHAdmin, self).save_models()

    # 重写queryset()或者get_list_display()，list view的权限也做到了对象级隔离
    def queryset(self):
        qs = super(QGXHAdmin, self).queryset()
        if self.request.user.is_superuser or is_admin(self.request.user):
            return qs
        try:
            return qs.filter(source=self.request.user.controlqgxh.source)
        except AttributeError:
            return None


xadmin.site.register(QGXH, QGXHAdmin)


class TECHAdmin(NewNewsBaseClass):
    pass


xadmin.site.register(TECH, TECHAdmin)


class NewsAdmin(NewNewsBaseClass):
    pass


xadmin.site.register(News, NewsAdmin)


class ChinaTopNewsAdmin(NewNewsBaseClass):
    pass


xadmin.site.register(ChinaTopNews, ChinaTopNewsAdmin)
class YqfkAdmin(NewNewsBaseClass):
    pass


xadmin.site.register(YQFK, YqfkAdmin)

class AgencyJgAdmin(NewOrgBaseClass):
    pass


xadmin.site.register(AgencyJg, AgencyJgAdmin)


class AgencyDfkxAdmin(NewOrgBaseClass):
    pass


xadmin.site.register(AgencyDfkx, AgencyDfkxAdmin)


class AgencyQgxhAdmin(NewOrgBaseClass):
    pass


xadmin.site.register(AgencyQgxh, AgencyQgxhAdmin)



class KxLeadersClass(object):
    # 显示的字段
    list_display = ['name', 'hidden']
    # 每页显示的数量
    list_per_page = 100
    list_display_links = ['name']
    # 操作选项
    actions_on_top = True
    # 搜索器
    search_fields = ['name']
    # 显示
    fields = ['name', 'hidden']
    # 排序
    ordering = ('id',)


xadmin.site.register(KxLeaders, KxLeadersClass)


# 权限管理的下放
class ControlQgxhAdmin(object):
    pass


xadmin.sites.site.register(ControlQgxh, ControlQgxhAdmin)


class ControlDfkxAdmin(object):
    pass


xadmin.sites.site.register(ControlDfkx, ControlDfkxAdmin)
