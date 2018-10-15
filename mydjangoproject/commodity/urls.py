from django.conf.urls import include, url
from django.contrib import admin
from commodity import views
urlpatterns = [
    #通过url函数设置url路由配置项
    url(r'^$', views.index,name='index')
]
