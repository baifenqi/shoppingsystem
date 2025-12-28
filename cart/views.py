# views.py
# 视图函数定义文件，处理购物车相关的HTTP请求和响应
# 导入Django快捷函数模块
from django.shortcuts import render, get_object_or_404, redirect
# 导入登录验证装饰器
from django.contrib.auth.decorators import login_required
# 导入Django消息框架
from django.contrib import messages
# 导入JSON响应类
from django.http import JsonResponse
from django.contrib.auth import get_user_model  # 添加这行
# 导入当前应用的模型
from .models import Cart, CartItem
# 导入产品模型（假设products应用已注册）
from products.models import Product
# 导入JSON处理模块
import json
# 获取用户模型
User = get_user_model()  # 添加这行

@login_required  # 要求用户登录才能访问
def cart_detail(request):
    """显示购物车详情的视图函数"""
    # 获取当前用户的购物车，如果不存在则创建
    cart, created = Cart.objects.get_or_create(user=request.user)
    # 使用select_related预取关联的商品数据，优化数据库查询
    cart_items = cart.items.select_related('product').all()
    # 准备模板上下文数据
    context = {
        'cart': cart,  # 购物车对象
        'cart_items': cart_items,  # 购物车项列表
        'total_price': cart.total_price()  # 购物车总金额
    }
    # 渲染并返回购物车详情模板
    return render(request, 'cart/cart_detail.html', context)

@login_required  # 要求用户登录才能访问
def add_to_cart(request, product_id):
    """添加商品到购物车的视图函数"""
    # 只处理POST请求
    if request.method == 'POST':
        # 根据商品ID获取商品对象，如果不存在则返回404
        product = get_object_or_404(Product, id=product_id)
        # 获取当前用户的购物车，如果不存在则创建
        cart, created = Cart.objects.get_or_create(user=request.user)
        # 从POST数据中获取商品数量，默认值为1
        quantity = int(request.POST.get('quantity', 1))
        
        # 检查库存是否充足
        if quantity > product.stock:
            # 库存不足时显示错误消息
            messages.error(request, f'库存不足，当前库存: {product.stock}')
            # 重定向回商品详情页
            return redirect('products:product_detail', product_id=product_id)
        
        # 获取或创建购物车项
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,  # 关联购物车
            product=product,  # 关联商品
            defaults={'quantity': quantity}  # 创建时的默认数量
        )
        
        # 如果购物车项已存在（未创建新的），则增加数量
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # 添加成功消息
        messages.success(request, f'已添加{product.name}到购物车')
        # 重定向到购物车详情页
        return redirect('cart:cart_detail')
    
    # 如果不是POST请求，重定向到商品列表页
    return redirect('products:product_list')

@login_required  # 要求用户登录才能访问
def remove_from_cart(request, item_id):
    """从购物车移除商品的视图函数"""
    # 根据购物车项ID获取购物车项，确保属于当前用户
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    # 获取商品名称用于消息显示
    product_name = cart_item.product.name
    # 删除购物车项
    cart_item.delete()
    # 添加成功消息
    messages.success(request, f'已从购物车移除{product_name}')
    # 重定向到购物车详情页
    return redirect('cart:cart_detail')

@login_required  # 要求用户登录才能访问
def update_cart_item(request, item_id):
    """更新购物车商品数量的视图函数（支持AJAX请求）"""
    # 检查是否为AJAX POST请求
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 解析JSON请求体
        data = json.loads(request.body)
        # 从JSON数据中获取新的数量，默认值为1
        quantity = int(data.get('quantity', 1))
        
        # 根据购物车项ID获取购物车项，确保属于当前用户
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # 如果数量小于等于0，删除购物车项
        if quantity <= 0:
            cart_item.delete()
            # 返回JSON响应，包含成功标识和购物车信息
            return JsonResponse({
                'success': True,  # 操作成功标识
                'deleted': True,  # 已删除标识
                'cart_total': cart_item.cart.total_price(),  # 购物车总金额
                'item_count': cart_item.cart.item_count()  # 购物车商品数量
            })
        
        # 检查库存是否充足
        if quantity > cart_item.product.stock:
            # 库存不足时返回错误信息
            return JsonResponse({
                'success': False,  # 操作失败标识
                'error': f'库存不足，当前库存: {cart_item.product.stock}'
            })
        
        # 更新购物车项数量
        cart_item.quantity = quantity
        cart_item.save()
        
        # 返回JSON响应，包含更新后的购物车信息
        return JsonResponse({
            'success': True,  # 操作成功标识
            'item_total': cart_item.total_price(),  # 购物车项小计
            'cart_total': cart_item.cart.total_price(),  # 购物车总金额
            'item_count': cart_item.cart.item_count()  # 购物车商品数量
        })
    
    # 如果不是有效的AJAX POST请求，返回错误响应
    return JsonResponse({'success': False, 'error': '无效请求'}, status=400)

@login_required  # 要求用户登录才能访问
def clear_cart(request):
    """清空购物车的视图函数"""
    # 获取当前用户的购物车
    cart = get_object_or_404(Cart, user=request.user)
    # 获取购物车中商品的数量
    items_count = cart.items.count()
    # 删除购物车中的所有购物车项
    cart.items.all().delete()
    # 添加成功消息，显示清空的商品数量
    messages.success(request, f'已清空购物车，共移除{items_count}件商品')
    # 重定向到购物车详情页
    return redirect('cart:cart_detail')