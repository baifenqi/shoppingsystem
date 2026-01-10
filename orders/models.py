from django.db import models
from django.conf import settings
from products.models import Product  # 关联商品模型
from django.utils import timezone

# 订单状态选项（基础版）
ORDER_STATUS_CHOICES = (
    ('pending', '待付款'),
    ('paid', '已付款'),
    ('shipped', '已发货'),
    ('delivered', '已送达'),
    ('cancelled', '已取消'),
)

class Order(models.Model):
    """订单主表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 关联自定义用户模型
        on_delete=models.CASCADE,
        related_name='orders'
    )
    full_name = models.CharField('收货人姓名', max_length=100)
    phone = models.CharField('收货人电话', max_length=11)
    address = models.TextField('收货地址')
    total_price = models.DecimalField('订单总价', max_digits=10, decimal_places=2)
    status = models.CharField(
        '订单状态',
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']  # 按创建时间倒序

    def __str__(self):
        return f'订单 {self.id} - {self.user.username}'

class OrderItem(models.Model):
    """订单项（关联订单和商品）"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    price = models.DecimalField('商品单价', max_digits=10, decimal_places=2)  # 下单时的价格（防止商品价格变动）
    quantity = models.PositiveIntegerField('购买数量', default=1)

    class Meta:
        verbose_name = '订单项'
        verbose_name_plural = '订单项'

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    # 计算订单项总价
    @property
    def total_price(self):
        return self.price * self.quantity