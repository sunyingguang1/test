from django.contrib import admin
from commodity.models import *
# #注册模型
# #自定义模型管理类
# class BookInfoAdmin(admin.ModelAdmin):
#     '''图书模型管理类'''
#     list_display = ['id','btitle','bpubdate']
# class HeroInfoAdmin(admin.ModelAdmin):
#     list_display = ['id','hname','hgender','hconcent','hbookinfo']
#
# # Register your models here.
# admin.site.register(BookInfo,BookInfoAdmin)
# admin.site.register(HeroInfo,HeroInfoAdmin)