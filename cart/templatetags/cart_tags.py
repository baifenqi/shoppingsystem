from django import template
from cart.models import Cart
from decimal import Decimal

register = template.Library()

# 1. 购物车总价标签（适配你的Cart模型）
@register.simple_tag(takes_context=True)
def cart_total_price(context):
    """获取当前用户购物车的总价（Decimal类型）"""
    request = context['request']
    if not request.user.is_authenticated:
        return Decimal('0.00')
    
    try:
        cart = Cart.objects.get(user=request.user)
        return cart.total_price()
    except Cart.DoesNotExist:
        return Decimal('0.00')

# 2. 购物车商品数量标签（适配你的Cart模型）
@register.simple_tag(takes_context=True)
def cart_item_count(context):
    """获取当前用户购物车的商品总件数"""
    request = context['request']
    if not request.user.is_authenticated:
        return 0
    
    try:
        cart = Cart.objects.get(user=request.user)
        return cart.item_count()
    except Cart.DoesNotExist:
        return 0

# 3. 乘法过滤器（模板中计算商品小计）
@register.filter
def mul(value, arg):
    """乘法过滤器：处理Decimal/int/float类型的乘法，保证精度"""
    try:
        # 统一转为Decimal计算
        value_dec = Decimal(str(value)) if not isinstance(value, Decimal) else value
        arg_dec = Decimal(str(arg)) if not isinstance(arg, Decimal) else arg
        return value_dec * arg_dec
    except (ValueError, TypeError):
        return Decimal('0.00')