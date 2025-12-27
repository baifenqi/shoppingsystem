# users/urls.py
# 用户应用的URL路由配置文件，定义URL模式与视图函数的映射关系
from django.urls import path
from . import views

# 应用命名空间，用于URL反向解析时区分不同应用的同名URL
app_name = 'users'

# URL模式列表，Django会按照顺序匹配这些模式
urlpatterns = [
    # 当前登录用户个人中心URL（默认入口：空路径）
    # 访问 /users/ 直接映射到profile视图函数（应用根路径默认显示个人中心）
    # name='profile'用于模板中URL反向解析
    path('', views.profile, name='profile'),
    
    # 用户注册页面URL
    # "register/"路径映射到register视图函数
    # name='register'用于模板中URL反向解析
    path('register/', views.register, name='register'),
    
    # 用户登录页面URL
    # "login/"路径映射到user_login视图函数
    # 登录页面的表单提交通常指向此URL
    path('login/', views.user_login, name='login'),
    
    # 用户登出URL
    # "logout/"路径映射到user_logout视图函数
    # 个人中心的"退出登录"按钮通常指向此URL
    path('logout/', views.user_logout, name='logout'),
    
    # 查看其他用户资料URL
    # <str:username>捕获用户名作为字符串参数传递给profile_detail视图函数
    # 点击用户名跳转查看他人公开资料时指向此URL
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
]
