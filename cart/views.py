from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from .models import Cart, CartItem
from products.models import Product

# 1. 购物车详情视图（urls.py中引用的核心视图）
@login_required
def cart_detail(request):
    """展示当前用户的购物车详情"""
    # 获取或创建用户的购物车（OneToOne关系）
    cart, created = Cart.objects.get_or_create(user=request.user)
    # 获取购物车所有商品项
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.total_price(),  # 调用你的Cart模型的总价方法
        'item_count': cart.item_count(),    # 调用你的Cart模型的数量方法
    }
    return render(request, 'cart/cart_detail.html', context)

# 2. 添加商品到购物车
@login_required
def add_to_cart(request, product_id):
    """将商品添加到购物车（支持数量修改）"""
    product = get_object_or_404(Product, id=product_id)
    # 获取或创建购物车
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # 获取数量（默认1，支持POST传参）
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    
    # 获取或创建购物车项
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    # 如果购物车项已存在，更新数量
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'成功添加 {product.name} 到购物车！')
    # 跳转回商品详情页或购物车
    next_url = request.GET.get('next', 'cart:cart_detail')
    return redirect(next_url)

# 3. 从购物车移除商品
@login_required
def remove_from_cart(request, item_id):
    """从购物车移除指定商品项"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'已从购物车移除 {product_name}！')
    return redirect('cart:cart_detail')

# 4. 更新购物车商品数量（AJAX接口，可选）
@login_required
def update_cart_quantity(request, item_id):
    """更新购物车商品数量（支持AJAX请求）"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # 返回更新后的小计和总价
        return JsonResponse({
            'status': 'success',
            'subtotal': float(cart_item.total_price()),
            'total_price': float(cart_item.cart.total_price()),
            'item_count': cart_item.cart.item_count()
        })
    except ValueError:
        return JsonResponse({'status': 'error', 'message': '数量必须是数字'})

# 5. 清空购物车
@login_required
def clear_cart(request):
    """清空当前用户的购物车"""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    
    messages.success(request, '购物车已清空！')
    return redirect('cart:cart_detail')