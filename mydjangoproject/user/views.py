from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from user.models import *
from utils.user_until import my_md5
from django.core.urlresolvers import reverse  # 反向解析url
import urllib
from utils import user_until
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
from django.conf import settings
import re
from django.views.decorators.csrf import csrf_exempt#用视图方法绕过csrf
from django.views.generic import View

from celery_tasks.tasks import send_register_active_email


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import SignatureExpired,BadSignature
from django.core.mail import send_mail

from django.contrib.auth import authenticate,login

# Create your views here.
class RegisterView(View):
    def get(self,request):
        '''注册页面'''
        return render(request, 'user/register.html')
    def post(self,request):
        '''注册处理'''
        request_info = request.POST
        # 通过字典的键获取值
        user_name = request_info.get('user_name', '').strip()
        user_pwd = request_info.get('pwd', '').strip()
        user_cpwd = request_info.get('cpwd', '').strip()
        user_email = request_info.get('email', '').strip()
        user_allow = request_info.get('allow')
        validate_code=request_info.get('validate_code').strip()
        print(user_name)
        print(user_pwd)
        # 判断
        print(validate_code)
        if validate_code=='':
            print('11')
            return render(request, 'user/register.html', {'error_validate_code': '验证码必填'})

        elif validate_code!=request.session["validate_code"]:
            print('22')
            return render(request, 'user/register.html', {'error_validate_code': '验证码错误'})

        if not all([user_name, user_pwd, user_cpwd, user_email]):
            print('1')
            return render(request, 'user/register.html', {'errmsg': '数据不完整'})

        if not 5 <= len(user_name) <= 20:
            print('2')
            return render(request, 'user/register.html', {'errmsg': '用户名必须5-20个字符'})

        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            user = None
        if user:
            print('3')
            return render(request, 'user/register.html', {'errmsg': '用户名已存在'})

        if not 8 <= len(user_pwd) <= 20:
            print('4')
            return render(request, 'user/register.html', {'errmsg': '密码必须为8-20个字符'})

        if user_pwd != user_cpwd:
            print('5')
            return render(request, 'user/register.html', {'errmsg': '两次密码不一样'})

        if re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", user_email) == None:
            print('6')
            return render(request, 'user/register.html', {'errmsg': '邮箱格式错误'})

        if user_allow != 'on':
            print('7')
            return render(request, 'user/register.html', {'errmsg': '请勾选同意'})


        # 在数据库中新增
        else:
            print('8')
            user = User.objects.create_user(username=user_name, password=user_pwd, email=user_email)
            user.is_active = 0
            user.save()
            #发送激活邮件，包含激活链接：http://192.168.12.164/user/active/3
            #激活链接中需要包含用户的身份信息，并且要把身份信息进行加密

            #加密用户的身份信息，生成激活token
            serializer=Serializer(settings.SECRET_KEY,3600)
            info={'confirm':user.id}
            token=serializer.dumps(info).decode('utf-8')
            print(token)
            encryption_url = "http://192.168.12.164:8888/user/active/%s" % token
            print('********')
            print(info)

            #发邮件
            send_register_active_email.delay(user_email,user_name,encryption_url)
            # subject='天天生鲜会员注册'
            # message=''
            # sender=settings.EMAIL_FORM
            # receiver=[user_email]
            # html_message='<h1>%s,欢迎成为天天生鲜会员<h1>请点击下面链接激活您的账户<br/><a href="%s" >%s</a>'%(user_name,encryption_url,encryption_url)
            # send_mail(subject,message,sender,receiver,html_message=html_message)
            # print('2222222222222')

            return HttpResponseRedirect(reverse('user:login'))
class Activeview(View):
    '''用户激活'''
    def get(self,request,token):
        '''进行用户激活'''
        serializer=Serializer(settings.SECRET_KEY,3600)
        print('111111')
        try:
            info=serializer.loads(token)
            print('********')
            print(token)
            #获取用户id信息
            user_id=info['confirm']
            #根据id获取用户信息
            user=User.objects.get(id=user_id)
            user.is_active=1
            user.save()
            return HttpResponseRedirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
        except BadSignature as e:
            return HttpResponse('激活链接非法')

class LoginView(View):
    def get(self,request):
        #判断是否记住了用户名
        if 'username' in request.COOKIES:
            user_name=request.COOKIES['username']
            checked = 'checked'
        else:
            user_name=''
            checked=''
        return render(request,'user/login.html',{'username':user_name,'checked':checked})
    def post(self,request):
        username=request.POST.get('username')
        password=request.POST.get('pwd')
        remember_name=request.POST.get('remember_name')
        #校验数据
        if not all([username,password]):
            return render(request, 'user/login.html',{'errormsg':'数据不完整'})
        #业务处理：登录校验
        user=authenticate(username=username,password=password)
        if user is not None:
            if user.is_active==1:
                #记住用户登录状态
                login(request,user)

                resp=HttpResponseRedirect(reverse('commodity:index'))

                if remember_name=='on':
                    print('1111')
                    resp.set_cookie('username',username,7*24*3600)
                else:
                    resp.delete_cookie('username')
                return resp
            else:
                return render(request, 'user/login.html', {'errormsg': '请登录邮箱完成激活'})
        else:
            return render(request, 'user/login.html', {'errormsg': '用户名密码错误'})


# def login(request):
#     if request.method == 'GET':
#     # 获取cookie
#     # remember_user_name=request.COOKIES.get('remember_user_name','')
#     # error_validate=urllib.parse.unquote(request.COOKIES.get('error_validate',''))
#     # error_user_name=urllib.parse.unquote(request.COOKIES.get('error_user_name',''))
#     # error_user_pwd = urllib.parse.unquote(request.COOKIES.get('error_user_pwd',''))
#     # # request.set_cookie('error_user_name', urllib.parse.quote('用户名不存在'),0)
#
#
#     # return render(request,'user/login.html',{'remember_user_name':remember_user_name,'error_validate':error_validate,'error_user_name':error_user_name,'error_user_pwd':error_user_pwd})
#     # a = request.session.get('remember_user_name')
#     #
#     # b =request.session.get('remember_user_pwd')
#     # print(b)
#     # if a!=None and b!=None :
#     #     return HttpResponseRedirect(reverse('x:y2'))
#         return render(request, 'user/login.html')
#     elif request.method == 'POST':
#         username=request.POST.get('username')
#         pwd = request.POST.get('pwd')
#         #     resp = HttpResponseRedirect(reverse('userr:login'))
#         #     # resp.delete_cookie('error_validate')
#         #     # resp.delete_cookie('error_user_name')
#         #     # resp.delete_cookie('error_user_pwd')
#         # # #获取模板中填写的验证码
#         #     validate=request.POST.get('validate','').strip().lower()
#         #
#         #     if validate=='':
#         #         resp.set_cookie('error_validate',urllib.parse.quote('验证码必填'))
#         #
#         #         return resp
#         #
#         #     elif validate!=request.session["validate_code"]:
#         #         resp.set_cookie('error_validate',urllib.parse.quote('验证码错误'))
#         #         return resp
#         #
#         #     user_name = request.POST.get('user_name', '').strip()
#         #     user_pwd = request.POST.get('user_pwd', '').strip()
#         #     user_pwd = my_md5(user_pwd)
#         #     remember = request.POST.get('remember')
#         #
#         #     # print(remember)
#         #
#         #     if user_name=='':
#         #         resp.set_cookie('error_user_name',urllib.parse.quote('用户名非空'))
#         #         return resp
#         #
#         #     elif not User.objects.filter(name=user_name):
#         #         resp.set_cookie('error_user_name',urllib.parse.quote('用户名不存在'))
#         #         return resp
#         #     elif user_pwd=='':
#         #         resp.set_cookie('error_user_pwd', urllib.parse.quote('密码必填'))
#         #         return resp
#         #
#         #     elif not User.objects.filter(pwd=user_pwd):
#         #         resp.set_cookie('error_user_pwd', urllib.parse.quote('密码错误'))
#         #         return resp
#         #
#         #                 # resp1=HttpResponseRedirect(reverse('x:y1'))
#         user = User.objects.filter(username=username, password=pwd,is_active=1)
#         if len(user)!=None:
#             print(user)
#             print(type(user))
#             # if user[0].is_active==1:
#             return HttpResponseRedirect(reverse('user:user_center_info'))
#         else:
#             return HttpResponse('请登录邮箱激活账户')
#         #                 # return book_views.show(request)#转发请求
#         #                 # 重定向改变url发送请求两次
#         #                 #     return HttpResponseRedirect(reverse('x:y1'))
#         #                 #     resp = HttpResponseRedirect(reverse('x:y1'))
#         #                 # 判断是否点击记住密码
#         #                 request.session['remember_user_id'] = user[0].id
#         #                 #判断是否跳转到上一次的books页面
#         #                 url_dest=request.COOKIES.get('url_dest')
#         #                 if url_dest:
#         #                     resp1=HttpResponseRedirect(url_dest)
#         #                     #用完之后删除cookie防止下次进入直接跳转
#         #                     resp1.delete_cookie('url_dest')
#         #                 else:
#         #                     resp1=HttpResponseRedirect(reverse('commodity:index'))
#         #                         #记住用户名
#         #                 if remember == '1':
#         #                         resp1.set_cookie('remember_user_name',user_name,3600*24*7)
#         #                 else:
#         #                         resp1.set_cookie('remember_user_name', user_name, 0)
#         #                         # return resp



def validate_code(request):
    # 定义变量，用于画面的背景色、宽、高
    # bgcolor = (random.randrange(256), random.randrange(256), random.randrange(256))
    bgcolor = (255,255,255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 200):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'abcd123efgh456ijklmn789opqr0stuvwxyzABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]

    #保存到sesison
    request.session["validate_code"] = rand_str.lower()
    print(rand_str)

    # 构造字体对象
    font = ImageFont.truetype(settings.FONT_STYLE, 23)
    # 绘制4个字
    for i in range(4):
        # 构造字体颜色
        fontcolor = (255, random.randrange(0, 100), random.randrange(0, 100))
        draw.text((5+23*i, 2), rand_str[i], font=font, fill=fontcolor)

    # 释放画笔
    del draw

    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'images/png')

def user_center_info(request):
    return render(request,'user/user_center_info.html')

def cart(request):
    return render(request,'user/cart.html')

def user_center_order(request):
    return render(request,'user/user_center_order.html')