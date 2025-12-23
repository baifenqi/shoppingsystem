# products/signals.py
"""
商品系统信号处理模块
本文件定义Django信号处理器，用于在模型保存、更新、删除等操作前后执行特定逻辑
信号机制允许解耦应用程序组件，实现事件驱动的编程模型
"""

# 导入Django信号模块
# post_save: 对象保存后触发的信号
# pre_save: 对象保存前触发的信号  
# post_delete: 对象删除后触发的信号
from django.db.models.signals import post_save, pre_save, post_delete

# 导入信号接收器装饰器，用于将函数注册为信号处理器
from django.dispatch import receiver

# 导入Django数据库模型基类
from django.db import models

# 从当前应用的models模块导入需要处理的模型
from .models import Product, Inventory


@receiver([post_save, post_delete], sender=Inventory)
def update_product_stock(sender, instance, **kwargs):
    """
    Inventory库存信号处理器
    
    功能：当Inventory模型实例保存（创建或更新）或删除时，自动更新对应商品的总库存
    
    触发时机：
    1. 创建新SKU库存（post_save + created=True）
    2. 更新现有SKU库存数量（post_save + created=False）
    3. 删除SKU库存记录（post_delete）
    
    信号参数说明：
    sender: 发送信号的模型类，这里固定为Inventory
    instance: 触发信号的具体Inventory实例对象
    **kwargs: 额外的信号参数
        - created: 仅post_save信号有，布尔值，True表示新建，False表示更新
        - update_fields: 仅post_save信号可能有，更新的字段列表
    
    处理逻辑：
    1. 从Inventory实例获取关联的Product对象
    2. 聚合计算该Product所有SKU的库存总和
    3. 比较当前Product库存与计算的总库存
    4. 如果不同则更新Product的stock字段
    
    设计目的：
    保持Product.total_stock与Inventory.sum(count)的一致性
    避免手动管理库存时可能出现的数据不一致
    """
    
    # 获取当前Inventory实例关联的商品对象
    product = instance.product
    
    # 使用聚合查询计算该商品所有SKU的库存总和
    # inventory_items是通过Product模型中related_name='inventory_items'定义的反向关系管理器
    # aggregate()执行聚合操作，models.Sum('count')对count字段求和
    # 如果没有任何SKU，则total为None，通过or 0转为0
    total_stock = product.inventory_items.aggregate(
        total=models.Sum('count')
    )['total'] or 0
    
    # 安全性检查：确保Product对象有stock属性
    # 只有在库存发生变化时才更新，避免不必要的数据库操作
    if hasattr(product, 'stock') and product.stock != total_stock:
        # 更新商品总库存字段
        product.stock = total_stock
        
        # 使用update_fields参数只更新stock字段
        # 优点：
        # 1. 提高性能，避免更新所有字段
        # 2. 避免触发其他可能基于save()的信号处理器
        # 3. 减少数据库锁竞争
        product.save(update_fields=['stock'])


# 预留信号处理器示例（当前未启用，可根据需要添加）：

# @receiver(post_save, sender=Product)
# def create_default_inventory(sender, instance, created, **kwargs):
#     """
#     商品创建时自动创建默认库存记录
#     当新建商品时，自动创建一个基本的Inventory记录
#     
#     参数说明：
#     created: 布尔值，True表示新创建，False表示更新
#     """
#     if created:
#         # 创建默认库存，数量为0
#         Inventory.objects.create(
#             product=instance,
#             count=0,
#             sku=f"{instance.sku}-DEFAULT"
#         )


# @receiver(pre_save, sender=Product)
# def update_product_status(sender, instance, **kwargs):
#     """
#     商品保存前自动更新状态
#     例如：当库存为0时自动将状态改为缺货
#     
#     注意：pre_save信号在save()方法之前触发
#     """
#     if instance.stock == 0 and instance.status == 'published':
#         # 库存为0的已上架商品自动改为缺货状态
#         instance.status = 'out_of_stock'


# @receiver(post_save, sender=Product)
# def send_product_notification(sender, instance, created, **kwargs):
#     """
#     商品上架时发送通知
#     例如：新商品上架时通知管理员或订阅用户
#     """
#     if created and instance.status == 'published':
#         # 这里可以添加发送邮件、消息队列等逻辑
#         pass


# 信号注册说明：
# 信号处理器需要连接到Django的AppConfig.ready()方法
# 当前信号已在products/apps.py的ready()方法中导入注册


# 信号使用最佳实践：
# 1. 保持信号处理器轻量级，避免复杂业务逻辑
# 2. 注意信号递归调用问题
# 3. 在测试环境中可能需要断开某些信号
# 4. 考虑使用事务确保数据一致性


# 当前信号架构优势：
# 1. 自动维护库存一致性
# 2. 业务逻辑与模型操作解耦
# 3. 易于扩展新的业务规则
# 4. 提高代码可维护性


# 注意：如果需要添加新的信号处理器，请在products/apps.py的ready()方法中导入