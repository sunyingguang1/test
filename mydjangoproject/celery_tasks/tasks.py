#使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

import os
import django
#初始化django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mydjangoproject.settings")
django.setup()


#创建一个celery类的对象
app=Celery('celery_tasks.tasks',broker='redis://192.168.12.164:6379/8')


@app.task
#定义任务函数
def send_register_active_email(to_email,username,encryption_url):
    '''发送激活邮件'''
    # 发邮件
    subject = '天天生鲜会员注册'
    message = ''
    sender = settings.EMAIL_FORM
    receiver = [to_email]
    html_message = '<h1>%s,欢迎成为天天生鲜会员<h1>请点击下面链接激活您的账户<br/><a href="%s" >%s</a>' % (
    username,encryption_url, encryption_url)
    send_mail(subject, message, sender, receiver, html_message=html_message)