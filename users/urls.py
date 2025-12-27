# users/urls.py
# 用户URL路由配置
# 定义users应用的URL模式
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'  # 应用命名空间

urlpatterns = [
    # 用户注册
    path('register/', views.register, name='register'),
    
    # 用户登录
    path('login/', views.user_login, name='login'),
    
    # 用户登出
    path('logout/', views.user_logout, name='logout'),
    
    # 用户个人中心
    path('profile/', views.profile, name='profile'),
    
    # 查看其他用户资料
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    
    # Django内置认证视图（可选）
    # 密码重置
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name='password_reset'),
    
    # 密码重置完成
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    
    # 密码重置确认
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    # 密码重置完成
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
]