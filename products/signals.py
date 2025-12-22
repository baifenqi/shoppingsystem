# products/signals.py
# 信号处理模块
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import models
from .models import Product, Inventory


@receiver([post_save, post_delete], sender=Inventory)
def update_product_stock(sender, instance, **kwargs):
    """
    当Inventory变化时，更新Product的总库存
    """
    product = instance.product
    total_stock = product.inventory_items.aggregate(
        total=models.Sum('count')
    )['total'] or 0
    if hasattr(product, 'stock') and product.stock != total_stock:
        product.stock = total_stock
        product.save(update_fields=['stock'])


# 如果需要更多信号，可以在这里添加
# 暂时保持简单