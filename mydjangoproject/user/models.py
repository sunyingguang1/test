from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel

'''
继承AbstractUser:用它的属性
继承BaseModel：共有的属性
'''


class User(AbstractUser,BaseModel):
    '''用户模型类'''
    class Meta:
        db_table='df_user'
        verbose_name='用户'
        verbose_name_plural=verbose_name

class Adress(BaseModel):
    '''定义地址模型类'''
    user=models.ForeignKey('User',verbose_name='所属账户')
    receivers=models.CharField(max_length=20,verbose_name='收件人')
    address=models.CharField(max_length=256,verbose_name='收获地址')
    postcode=models.CharField(max_length=6,verbose_name='邮政编码',null=True)
    phone=models.CharField(max_length=11,verbose_name='联系电话')
    is_default=models.BooleanField(default=False,verbose_name='是否为默认')
    class Meta:
        db_table='df_adress'
        verbose_name='地址'
        verbose_name_plural=verbose_name