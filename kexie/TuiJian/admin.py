from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.html import format_html
from .models import  *
from django.utils.translation import ugettext_lazy as new_fliter
from django.contrib.admin import SimpleListFilter
from django.shortcuts import reverse, render
#用户可以批量操作
from django.contrib import admin, messages
from django import forms
from .forms import *
import datetime


class OrgBaseClass(admin.ModelAdmin):
    # 显示的字段
    list_display = ['number', 'department']
    #每页显示的数量
    list_per_page = 30
    list_display_links = ['number', 'department']
    #操作选项
    actions_on_top = True
    #搜索器
    search_fields = ['number', 'department']
    #显示
    fields = ['number', 'department']
    #排序
    ordering = ('id',)
    #设置普通用户不可编辑字段，指进入详情也不可编辑
    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        if request.user.is_superuser:
            self.readonly_fields = []
        return self.readonly_fields
    readonly_fields = ('number', 'department')

class  NewsBaseClass ( admin.ModelAdmin ) :

    #设置普通用户不可编辑字段，指进入详情也不可编辑
    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        if request.user.is_superuser:
            self.readonly_fields = []
        return self.readonly_fields
    readonly_fields = ('like', 'comment')

    #显示缩略图
    def img_data(self, obj):
        if obj.img and hasattr(obj.img, 'url'):
            if 'http' in obj.img.url:
                return format_html('<img src="{0}" width="150px" height="150px"/>'.format(obj.img))
            else:
                return format_html('<img src="{0}" width="150px" height="150px"/>'.format(obj.img.url))
        else:
            return None
    img_data.short_description = '新闻图片'

    # 显示的字段
    list_display = ['title','img_data','time', 'source','priority', 'hidden']
    list_editable = ['priority', 'hidden']
    #每页显示的数量
    list_per_page = 30
    #跳转连接
    #试着重新list_display_links
    def my_time(self,request,obj):
        return render(request,'news.html',{'news_list':obj})

    list_display_links = ['title','source',"time"]

    #设置空值
    empty_value_display ='无'
    #操作选项
    actions_on_top = True

    #搜索器
    search_fields = ['title', 'time', 'source','content']
    #跳转字段
    #fields = ['time']
    #分组显示
    fieldsets = (
        ('基本', {'fields': ['title', 'img','time','source']}),
        ('高级', {
            'fields': ['content','like', 'comment','url','author','label','hidden','keywords'],
            'classes': ('collapse',)  # 是否折叠显示
        })
    )
    ordering = ('-time',)

    #重写右边栏目的时间过滤器，使时间按照倒序
    class VersionFilter(SimpleListFilter):
        title = new_fliter('时间')

        parameter_name = 'time'

        def lookups(self, request, model_admin):
            qs = model_admin.get_queryset(request)
            return [(i, i) for i in qs.values_list('time', flat=True).distinct().order_by('-time')]

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(time__exact=self.value())
    #过滤器
    list_filter = ['source',VersionFilter]

    #自定义的action函数
    # 新建一个批量操作的函数，其中有三个参数：
    # 第一个参数是模型管理类，第二个request是请求，第三个queryset表示你选中的所有记录，
    # 这个函数里面会处理所有选中的queryset，所以要在操作之前用搜索或者过滤来选出需要修改的记录
    #批量删除删除图片

    def del_imgs(self, request, queryset):
        queryset.update(img=None)
        messages.success(request, "删除图片成功")

    del_imgs.short_description = "删除图片"

    #批量改变优先级
    def change_priority(self,request,queryset):
        queryset.update(priority=0)
        messages.success(request, "优先级全部被设置为0")

    change_priority.short_description = "优先级调整为0"

    #批量修改数据的表单
    class data_src_form(forms.forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        change= forms.CharField(max_length=255,required=False)
        change.label="请填写需要修改的值"

    #修改时间
    def update_time(self, request, queryset):
        return self.update_data(request=request, queryset=queryset,value='时间')
    update_time.short_description = '修改新闻时间'

    # 修改数据来源
    def update_source(self, request, queryset):
        return self.update_data(request=request, queryset=queryset,value='来源')

    update_source.short_description = '修改新闻来源'
    #任意调整优先级
    def update_priority(self, request, queryset):
        return self.update_data(request=request, queryset=queryset,value='优先级')

    update_priority.short_description = '修改新闻推荐优先级'

    #修改数据的执行函数
    def update_data(self, request, queryset,value):
        form = None
        if 'cancel' in request.POST:
            return HttpResponseRedirect(request.get_full_path())
        elif 'change' in request.POST:
            form = self.data_src_form(request.POST)

            if form.is_valid():
                change = form.cleaned_data['change']
                for case in queryset:
                    #只有正确的时间能被写入
                    if value == '时间':
                        print(value)
                        try:
                            datetime.datetime.strptime(change, "%Y-%m-%d")
                            flag =True
                        except:
                            flag = False
                        if flag:
                            case.time = change
                        else:
                            messages.warning(request, "时间格式错误")
                            return render(request, 'updateData.html',
                                          {'objs': queryset, 'form': form, 'path': request.get_full_path(),
                                           'action': 'update_time', 'title': '批量修改新闻的时间'.format('..')})
                    elif value =='来源':
                        case.source = change
                    elif value =='优先级':
                        case.priority =value
                    case.save()
                self.message_user(request, "%s successfully updated." % queryset.count())
                return HttpResponseRedirect(request.get_full_path())
            else:
                messages.warning(request, "请选择数据源")
                form = None
        if not form:
            form = self.data_src_form(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
            if value =='时间':
                return render(request, 'updateData.html',
                              {'objs': queryset, 'form': form, 'path':request.get_full_path(),
                                                       'action': 'update_time', 'title': '批量修改新闻的时间'.format('..')})
            elif value =='来源':
                return render(request, 'updateData.html',
                              {'objs': queryset, 'form': form, 'path':request.get_full_path(),
                                                       'action': 'update_source', 'title': '批量修改新闻的来源'.format('..')})
            elif value =='优先级':
                return render(request, 'updateData.html',
                              {'objs': queryset, 'form': form, 'path':request.get_full_path(),
                                                       'action': 'update_priority', 'title': '批量修改新闻推荐优先级'.format('..')})
    #自定义的action
    actions = [del_imgs,change_priority,update_time,update_source,update_priority]
    # #设置字段的显示高和宽，这里重新后，详情页面字段不显示verbose_name，并且设置的blank属性就失效了
    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     # This method will turn all TextFields into giant TextFields
    #     if isinstance(db_field, models.CharField):
    #         return forms.CharField(widget=forms.Textarea(attrs={'rows':'1', 'cols': '23'}))
    #     return super(NewsBaseClass, self).formfield_for_dbfield(db_field, **kwargs)

@admin.register(KxLeaders)
class KxLeadersClass(admin.ModelAdmin):
    # 显示的字段
    list_display = ['name', 'hidden']
    #每页显示的数量
    list_per_page = 100
    list_display_links = ['name']
    #操作选项
    actions_on_top = True
    #搜索器
    search_fields = ['name']
    #显示
    fields = ['name', 'hidden']
    #排序
    ordering = ('id',)


@admin.register(KX)
class KXAdmin(NewsBaseClass):
    pass
@admin.register(DFKX)
class DFKXAdmin(NewsBaseClass):
    pass
@admin.register(QGXH)
class QGXHAdmin(NewsBaseClass):
    pass
@admin.register(TECH)
class TECHAdmin(NewsBaseClass):
    pass
@admin.register(News)
class NewsAdmin(NewsBaseClass):
    pass
@admin.register(ChinaTopNews)
class ChinaTopNewsAdmin(NewsBaseClass):
    pass
@admin.register(AgencyJg)
class AgencyJgAdmin(OrgBaseClass):
    pass
@admin.register(AgencyDfkx)
class AgencyDfkxAdmin(OrgBaseClass):
    pass
@admin.register(AgencyQgxh)
class AgencyQgxhAdmin(OrgBaseClass):
    pass




admin.site.site_header = '新闻管理系统'
admin.site.site_title = '新闻管理系统'
admin.site.index_title = '欢迎使用新闻管理系统'
