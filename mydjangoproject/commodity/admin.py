from django.contrib import admin
from commodity.models import *
# #注册模型
# #自定义模型管理类
admin.site.register(GoodType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
