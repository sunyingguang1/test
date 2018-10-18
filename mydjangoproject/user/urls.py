from django.conf.urls import include, url
from django.contrib import admin
from user import views
from django.contrib.auth.decorators import login_required#使用login_required 装饰器

urlpatterns = [
    url(r'^register$',views.RegisterView.as_view(),name='register'),#用户注册页面

    url(r'^login$',views.LoginView.as_view(),name='login'),#用户登录页面

    url(r'^logout$',views.LogoutView.as_view(),name='logout'),#用户退出页面

    url(r'^change1$',views.ChangePassword1.as_view(),name='change1'),#修改密码

    url(r'^change/(?P<token>.*)$',views.ChangePassword2.as_view(),name='change2'),#修改密码

    url(r'^active/(?P<token>.*)$',views.Activeview.as_view(),name='active'),#用户激活

    url(r'^validate_code$',views.validate_code,name='validate_code'),#验证码

    url(r'^$',views.UserInfoView.as_view(),name='user'),#用户中心-信息页

    url(r'^order$',views.UserOrderView.as_view(),name='order'),#用户中心-订单页

    url(r'^adress$',views.UserAdressView.as_view(),name='adress'),#用户中心-地址页

    url(r'^edit$',views.UserEditAdressView.as_view(),name='edit'),#用户中心-地址页

    url(r'adre/(?P<hid>\d+)$',views.UserEditAdreView.as_view(),name='adre'),
    # url(r'^$', login_required(views.UserInfoView.as_view()), name='user'),  # 用户中心-信息页
    #
    # url(r'^order$',login_required(views.UserOrderView.as_view()),name='order'),#用户中心-订单页
    #
    # url(r'^adress$',login_required(views.UserAdressView.as_view()),name='address'),#用户中心-地址页

    url(r'^cart$',views.UserCardView.as_view(),name='cart'),#购物车页面
]
