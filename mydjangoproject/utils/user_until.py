import hashlib
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader,RequestContext
from commodity.models import *
# Create your views here.
from django.core.urlresolvers import reverse
# from utils.user_until import my_login
import uuid
import os


def my_md5(value):
    '''
    密码加密
    :param value:
    :return:
    '''
    m=hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()
#登录装饰器
def my_login(func):
    def inner(*args,**kwargs):
        login_id = args[0].session.get('remember_user_id')
        if login_id:
            return func(*args,**kwargs)
        else:
            #记录之前的url
            resp=HttpResponseRedirect(reverse('userr:login'))
            resp.set_cookie('url_dest',args[0].get_full_path())
            return resp
    return inner

# def select_all(request):
#     login_id=request.session.get('remember_user_id')
#     if login_id:
#         book_list = BookInfo.objects.all()
#         return render(request,'book/book_list.html',{'book_list':book_list})
#     else:
#         return HttpResponseRedirect(reverse('userr:login'))

#文件上传名字处理
def do_file_name(file_name):
    return str(uuid.uuid1())+os.path.splitext(file_name)[1]