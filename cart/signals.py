# signals.py
# 信号处理文件，定义购物车应用中的信号接收器
# 信号用于在特定动作发生时执行相关操作，实现松耦合
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model  # 修改这行
from .models import Cart, CartItem
from products.models import Product
from django.core.cache import cache
# 获取用户模型
User = get_user_model()  # 添加这行

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """
    用户注册成功后自动创建购物车的信号接收器
    sender: 发送信号的模型（User）
    instance: 保存的User实例
    created: 是否为新建对象（True表示新建）
    **kwargs: 其他关键字参数
    """
    if created:  # 只在创建新用户时执行
        Cart.objects.create(user=instance)  # 为新用户创建购物车
        print(f"已为用户 {instance.username} 创建购物车")  # 控制台输出提示

@receiver(pre_delete, sender=CartItem)
def update_product_stock_on_remove(sender, instance, **kwargs):
    """
    从购物车删除商品时，如果购物车项数量大于0，理论上应恢复库存
    但实际项目中通常不在这里处理，而是在订单确认/取消时处理库存
    sender: 发送信号的模型（CartItem）
    instance: 要删除的CartItem实例
    **kwargs: 其他关键字参数
    """
    # 实际项目中，这里可以记录日志或执行其他清理操作
    # 注意：购物车删除不代表商品售出，所以不恢复库存
    pass

@receiver(post_save, sender=Product)
def clear_cart_cache_on_price_change(sender, instance, **kwargs):
    """
    商品价格变更时清除相关购物车缓存
    sender: 发送信号的模型（Product）
    instance: 保存的Product实例
    **kwargs: 其他关键字参数
    """
    # 清除与商品相关的购物车缓存
    cache_keys_to_delete = []
    # 查找所有包含此商品的购物车项
    cart_items = CartItem.objects.filter(product=instance)
    for item in cart_items:
        # 构造缓存键（假设购物车缓存键格式为'cart_{user_id}'）
        cache_key = f'cart_{item.cart.user.id}'
        cache_keys_to_delete.append(cache_key)
    
    # 删除所有相关缓存
    cache.delete_many(cache_keys_to_delete)
    print(f"商品 {instance.name} 价格变更，已清除相关购物车缓存")

@receiver(post_save, sender=CartItem)
def update_cart_timestamp(sender, instance, **kwargs):
    """
    购物车项变更时更新购物车的更新时间
    sender: 发送信号的模型（CartItem）
    instance: 保存的CartItem实例
    **kwargs: 其他关键字参数
    """
    cart = instance.cart  # 获取购物车项关联的购物车
    cart.save()  # 调用save()会自动更新updated_at字段
    # 注意：这里只更新updated_at，不修改其他字段