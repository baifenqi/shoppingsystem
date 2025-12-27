# users/views.py
# 用户视图函数
# 处理用户相关的HTTP请求和业务逻辑
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import CustomUser

def register(request):
    """用户注册视图函数"""
    if request.method == 'POST':  # 处理POST请求
        form = UserRegisterForm(request.POST)  # 实例化注册表单
        if form.is_valid():  # 表单验证通过
            user = form.save()  # 保存用户
            username = form.cleaned_data.get('username')  # 获取用户名
            messages.success(request, f'账号 {username} 创建成功！请登录')  # 成功消息
            return redirect('users:login')  # 重定向到登录页
    else:
        form = UserRegisterForm()  # 创建空表单
    return render(request, 'users/register.html', {'form': form})  # 渲染注册模板

def user_login(request):
    """用户登录视图函数"""
    if request.method == 'POST':  # 处理POST请求
        form = UserLoginForm(request, data=request.POST)  # 实例化登录表单
        if form.is_valid():  # 表单验证通过
            username = form.cleaned_data.get('username')  # 获取用户名
            password = form.cleaned_data.get('password')  # 获取密码
            user = authenticate(username=username, password=password)  # 验证用户
            if user is not None:  # 验证成功
                login(request, user)  # 登录用户
                messages.success(request, f'欢迎回来，{username}！')  # 欢迎消息
                # 重定向到用户个人中心或首页
                return redirect('users:profile')
    else:
        form = UserLoginForm()  # 创建空表单
    return render(request, 'users/login.html', {'form': form})  # 渲染登录模板

@login_required
def user_logout(request):
    """用户登出视图函数"""
    logout(request)  # 登出当前用户
    messages.info(request, '您已成功登出')  # 登出消息
    return redirect('home')  # 重定向到首页

@login_required
def profile(request):
    """用户个人中心视图函数"""
    if request.method == 'POST':  # 处理POST请求
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)  # 实例化表单
        if form.is_valid():  # 表单验证通过
            form.save()  # 保存更新
            messages.success(request, '个人资料已更新！')  # 成功消息
            return redirect('users:profile')  # 重定向回个人中心
    else:
        form = ProfileUpdateForm(instance=request.user)  # 创建表单实例
    return render(request, 'users/profile.html', {'form': form})  # 渲染个人中心模板

@login_required
def profile_detail(request, username):
    """查看其他用户资料视图函数"""
    user = CustomUser.objects.get(username=username)  # 获取指定用户
    return render(request, 'users/profile_detail.html', {'profile_user': user})  # 渲染用户资料模板