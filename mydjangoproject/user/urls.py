from django.conf.urls import include, url
from django.contrib import admin
from user import views

urlpatterns = [
    url(r'^register$',views.RegisterView.as_view(),name='register'),

    url(r'^login$',views.LoginView.as_view(),name='login'),

    url(r'^active/(?P<token>.*)$',views.Activeview.as_view(),name='active'),#用户激活

    url(r'^validate_code$',views.validate_code,name='validate_code'),#验证码

    url(r'^user_center_info$',views.user_center_info,name='user_center_info'),

    url(r'^cart$',views.cart,name='cart'),

    url(r'^user_center_order$',views.user_center_order,name='user_center_order'),
]
