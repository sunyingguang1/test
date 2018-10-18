from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from user.models import *
# from utils.user_until import my_md5
from django.core.urlresolvers import reverse  # 反向解析url
import urllib
from utils.Mixin import LoginRequiredMixin  # 封装as_view() 的Mixin
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
from django.conf import settings
import re
from django.views.decorators.csrf import csrf_exempt  # 用视图方法绕过csrf
from django.views.generic import View

from celery_tasks.tasks import send_register_active_email

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import SignatureExpired, BadSignature
from django.core.mail import send_mail

from django.contrib.auth import authenticate, login, logout


# Create your views here.
class RegisterView(View):
    def get(self, request):
        '''注册页面'''
        return render(request, 'user/register.html')

    def post(self, request):
        '''注册处理'''
        request_info = request.POST
        # 通过字典的键获取值
        user_name = request_info.get('user_name', '').strip()
        user_pwd = request_info.get('pwd', '').strip()
        user_cpwd = request_info.get('cpwd', '').strip()
        user_email = request_info.get('email', '').strip()
        user_allow = request_info.get('allow')
        validate_code = request_info.get('validate_code').strip()
        # 判断
        if validate_code == '':
            return render(request, 'user/register.html', {'error_validate_code': '验证码必填'})

        elif validate_code != request.session["validate_code"]:
            return render(request, 'user/register.html', {'error_validate_code': '验证码错误'})

        if not all([user_name, user_pwd, user_cpwd, user_email]):
            return render(request, 'user/register.html', {'errmsg': '数据不完整'})

        if not 5 <= len(user_name) <= 20:
            return render(request, 'user/register.html', {'errmsg': '用户名必须5-20个字符'})

        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'user/register.html', {'errmsg': '用户名已存在'})

        if not 8 <= len(user_pwd) <= 20:
            return render(request, 'user/register.html', {'errmsg': '密码必须为8-20个字符'})

        if user_pwd != user_cpwd:
            return render(request, 'user/register.html', {'errmsg': '两次密码不一样'})

        if re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", user_email) == None:
            return render(request, 'user/register.html', {'errmsg': '邮箱格式错误'})

        if user_allow != 'on':
            return render(request, 'user/register.html', {'errmsg': '请勾选同意'})


        # 在数据库中新增
        else:
            user = User.objects.create_user(username=user_name, password=user_pwd, email=user_email)
            user.is_active = 0
            user.save()
            # 发送激活邮件，包含激活链接：http://192.168.12.164/user/active/3
            # 激活链接中需要包含用户的身份信息，并且要把身份信息进行加密

            # 加密用户的身份信息，生成激活token
            serializer = Serializer(settings.SECRET_KEY, 3600)
            info = {'confirm': user.id}
            token = serializer.dumps(info).decode('utf-8')
            encryption_url = "http://192.168.12.164:8888/user/active/%s" % token

            # 发邮件
            send_register_active_email.delay(user_email, user_name, encryption_url)
            return HttpResponseRedirect(reverse('user:login'))


class Activeview(View):
    '''用户激活'''

    def get(self, request, token):
        '''进行用户激活'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取用户id信息
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return HttpResponseRedirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
        except BadSignature as e:
            return HttpResponse('激活链接非法')


class ChangePassword1(View):
    def get(self, requset):
        return render(requset, 'user/change_password1.html')

    def post(self, request):
        username = request.POST.get('user_name')
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        if pwd != cpwd:
            return render(request, 'user/change_password1.html', {'error': '两次输入密码不一致'})
        user = User.objects.get(username=username, email=email)
        if user is not None:
            serializer = Serializer(settings.SECRET_KEY, 3600)
            info = {'confirm': user.id, 'pwd': pwd}
            token = serializer.dumps(info).decode('utf-8')
            encryption_url = "http://192.168.12.164:8888/user/change/%s" % token
            # 发邮件
            send_register_active_email.delay(email, username, encryption_url)
            return HttpResponse('请前往邮箱验证')
        else:
            return render(request, 'user/change_password1.html', {'error': '用户名和邮箱不匹配'})


class ChangePassword2(View):
    def get(self, request, token):
        '''进行用户激活'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取用户id信息
            user_id = info['confirm']
            user_pwd = info['pwd']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.set_password(user_pwd)
            user.save()
            return HttpResponseRedirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
        except BadSignature as e:
            return HttpResponse('激活链接非法')


class LoginView(View):
    def get(self, request):
        # 判断是否记住了用户名
        if 'remember_username' in request.COOKIES:
            remember_username = urllib.parse.unquote(request.COOKIES.get('remember_username'))
            checked = 'checked'
        else:
            remember_username = ''
            checked = ''
        return render(request, 'user/login.html', {'remember_username': remember_username, 'checked': checked})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember_name = request.POST.get('remember_name')
        # 校验数据
        if not all([username, password]):
            return render(request, 'user/login.html', {'errormsg': '数据不完整'})
        # 业务处理：登录校验
        user = authenticate(username=username, password=password)
        print('user', user)
        if user is not None:
            if user.is_active == 1:
                # 记住用户登录状态
                login(request, user)

                next_url = request.GET.get('next')
                if next_url:
                    resp = HttpResponseRedirect(next_url)
                else:
                    resp = HttpResponseRedirect(reverse('commodity:index'))

                if remember_name == 'on':
                    resp.set_cookie('remember_username', urllib.parse.quote(username), max_age=7 * 24 * 3600)
                else:
                    resp.delete_cookie('remember_username')
                return resp
            else:
                return render(request, 'user/login.html', {'errormsg': '请登录邮箱完成激活'})
        else:
            return render(request, 'user/login.html', {'errormsg': '用户名密码错误'})


class LogoutView(LoginRequiredMixin, View):
    '''退出登录'''

    def get(self, request):
        # 清除用户session信息
        logout(request)
        return HttpResponseRedirect(reverse('commodity:index'))


def validate_code(request):
    # 定义变量，用于画面的背景色、宽、高
    # bgcolor = (random.randrange(256), random.randrange(256), random.randrange(256))
    bgcolor = (255, 255, 255)
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

    # 保存到sesison
    request.session["validate_code"] = rand_str.lower()
    print(rand_str)

    # 构造字体对象
    font = ImageFont.truetype(settings.FONT_STYLE, 23)
    # 绘制4个字
    for i in range(4):
        # 构造字体颜色
        fontcolor = (255, random.randrange(0, 100), random.randrange(0, 100))
        draw.text((5 + 23 * i, 2), rand_str[i], font=font, fill=fontcolor)

    # 释放画笔
    del draw

    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'images/png')


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        content = {"page": '1'}
        # 获取登录用户对应User对象
        user = request.user
        # 获取用户的收获地址
        try:
            adress1 = Adress.objects.get(user=user, is_default=True)
        except Adress.DoesNotExist:
            # 不存在收获地址
            adress1 = None
        return render(request, 'user/user_center_info.html', {'content': content, 'adress1': adress1})


class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        content = {"page": '2'}
        return render(request, 'user/user_center_order.html', {'content': content})


class UserAdressView(LoginRequiredMixin, View):
    def get(self, request):
        content = {"page": '3'}
        print('5')
        # 获取登录用户对应User对象
        user = request.user
        # 获取用户的收获地址
        try:
            adress1 = Adress.objects.get(user=user, is_default=True)
        except Adress.DoesNotExist:
            # 不存在收获地址
            adress1 = None
        return render(request, 'user/user_center_site.html', {'content': content, 'adress1': adress1})

    def post(self, request):
        # 接收数据
        adress = request.POST.get('adress')
        print(adress)
        recipients = request.POST.get('recipients')
        phone = request.POST.get('phone')
        postcode = request.POST.get('postcode')
        remember_adress = request.POST.get('remember_adress')
        # 校验数据
        if not all([recipients, adress, phone]):
            return render(request, 'user/user_center_site.html', {'error': '数据不完整'})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user/user_center_site.html', {'error': '手机号格式不正确'})
        # 业务处理
        # 如果用户有默认收获地址添加的地址不作为默认收获地址
        # 获取登录用户对应User对象
        user = request.user
        try:
            adress1 = Adress.objects.get(user=user, is_default=True)
        except Adress.DoesNotExist:
            # 不存在收获地址
            adress1 = None
        if adress1:
            is_default = False
        else:
            print('3')
            is_default = True
        # 添加地址
        Adress.objects.create(receivers=recipients,
                              address=adress,
                              postcode=postcode,
                              phone=phone,
                              is_default=is_default,
                              user=user,)
        print('4')
        # 返回应答刷新地址页面
        return HttpResponseRedirect(reverse('user:edit'))


class UserEditAdressView(LoginRequiredMixin,View):
    def get(self, request):
        adress = Adress.objects.all()
        return render(request, 'user/user_change_adress.html', {'adress': adress})


class UserEditAdreView(View):
    def get(self, request, hid):
        adress1 = Adress.objects.get(id=hid)
        return render(request, 'user/user_center_edit.html', {'adress1': adress1})

    def post(self, request, hid):
        recipients = request.POST.get('recipients')
        adress = request.POST.get('adress')
        phone = request.POST.get('phone')
        remember_adress = request.POST.get('remember_adress')
        user = Adress.objects.get(id=hid)
        if remember_adress == 'on':
            try:
                user1 = Adress.objects.get(is_default=True)
                user1.is_default = False
                user1.save()
            except:
                pass
            finally:
                user.receivers = recipients
                user.address = adress
                user.phone = phone
                user.is_default=True
                user.save()


        else:
            user.receivers = recipients
            user.address = adress
            user.phone = phone
            user.save()
        return HttpResponseRedirect(reverse('user:user'))


class UserCardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user/cart.html')
