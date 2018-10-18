from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import loader,RequestContext
from commodity.models import *
# Create your views here.
from django.core.urlresolvers import reverse
# from utils import user_until
from user.models import *
# from utils.user_until import do_file_name
import os
from django.conf import settings
from django.core.paginator import Paginator

from django.core.serializers import serialize
import json
# Create your views here.
#定义视图函数
#进行url配置，建立url地址和视图的对应关系
#http://192.168.227.129:8080
def index(request):
    #进行处理，和M和T进行交互

    return render(request,'commodity/index.html')
def test(request):
    goods_list=GoodType.objects.all()
    print(goods_list)
    return render(request,'commodity/test.html',{'good_list':goods_list})