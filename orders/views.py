from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from decimal import Decimal  # 新增：适配Decimal类型总价
from .models import Order, OrderItem
from cart.models import Cart  # 导入你的购物车模型

# 1. 创建订单（从购物车生成）
@login_required
def create_order(request):
    # 获取当前用户的购物车
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, '购物车为空，无法创建订单！')
        return redirect('cart:cart_detail')

    # 手动计算购物车总价（不依赖模板标签，更稳定）
    total_price = 0
    for item in cart.items.all():
        total_price += item.product.price * item.quantity

    if request.method == 'POST':
        # 获取表单提交的收货信息
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # 验证必填信息
        if not full_name or not phone or not address:
            messages.error(request, '收货人姓名、电话、地址不能为空！')
            return render(request, 'orders/create_order.html', {
                'total_price': total_price,
                'cart': cart
            })

        # 1. 创建订单主表
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            total_price=total_price
        )

        # 2. 从购物车生成订单项
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,  # 记录下单时的价格
                quantity=cart_item.quantity
            )

        # 3. 清空购物车
        cart.items.all().delete()

        messages.success(request, '订单创建成功！请尽快付款～')
        return redirect('orders:order_detail', order_id=order.id)

    # GET请求：展示创建订单页面（填写收货信息）
    return render(request, 'orders/create_order.html', {
        'total_price': total_price,
        'cart': cart
    })

# 2. 订单列表（当前用户）
@login_required
def order_list(request):
    # 只显示当前用户的订单
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })

# 3. 订单详情
@login_required
def order_detail(request, order_id):
    # 只允许查看自己的订单
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user:
        return HttpResponseForbidden('你无权查看该订单！')
    
    return render(request, 'orders/order_detail.html', {
        'order': order
    })

# 4. 简单的订单状态更新（可选，比如标记为已付款）
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [s[0] for s in Order.ORDER_STATUS_CHOICES]:
            order.status = new_status
            order.save()
            messages.success(request, '订单状态已更新！')
        else:
            messages.error(request, '无效的订单状态！')
        return redirect('orders:order_detail', order_id=order.id)
    return redirect('orders:order_detail', order_id=order.id)