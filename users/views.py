# users/views.py
# 用户视图函数
# 处理用户相关的HTTP请求和业务逻辑
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import CustomUser
from cart.models import Cart  
from orders.models import Order


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
    """用户个人中心视图函数（整合个人信息、购物车、订单）"""
    # 保留你原有：个人资料更新逻辑
    if request.method == 'POST':  # 处理POST请求（更新个人资料）
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)  # 实例化表单
        if form.is_valid():  # 表单验证通过
            form.save()  # 保存更新
            messages.success(request, '个人资料已更新！')  # 成功消息
            return redirect('users:profile')  # 重定向回个人中心
    else:
        form = ProfileUpdateForm(instance=request.user)  # 创建表单实例

    # ========== 新增：整合购物车+订单数据 ==========
    # 1. 组装用户基础信息（适配你的CustomUser模型）
    user_info = {
        'username': request.user.username,
        'email': request.user.email or '未绑定邮箱',
        # 适配你的CustomUser模型字段（如果没有phone则注释/修改）
        'phone': getattr(request.user, 'phone', '未绑定手机号'),
        'date_joined': request.user.date_joined.strftime('%Y-%m-%d'),  # 注册时间
    }
    
    # 2. 获取购物车信息（适配你的Cart模型）
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_info = {
        'items': cart.items.all(),  # 购物车商品列表
        'total_price': cart.total_price(),  # 购物车总价（调用你模型的方法）
        'item_count': cart.item_count(),  # 购物车商品数量（调用你模型的方法）
    }
    
    # 3. 获取订单信息（最近5条，按创建时间倒序）
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    all_orders_count = Order.objects.filter(user=request.user).count()  # 订单总数

    # ========== 组装最终上下文（保留原有form + 新增数据） ==========
    context = {
        'form': form,  # 原有：个人资料表单
        'user_info': user_info,  # 新增：用户基础信息
        'cart_info': cart_info,  # 新增：购物车信息
        'recent_orders': orders,  # 新增：最近订单
        'all_orders_count': all_orders_count,  # 新增：订单总数
    }
    
    return render(request, 'users/profile.html', context)  # 渲染个人中心模板

@login_required
def profile_detail(request, username):
    """查看其他用户资料视图函数"""
    user = get_object_or_404(CustomUser, username=username)  # 获取指定用户
    return render(request, 'users/profile_detail.html', {'profile_user': user})  # 渲染用户资料模板