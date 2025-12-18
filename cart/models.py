# models.py
# 数据模型定义文件，定义购物车相关的数据库模型
# 导入Django模型模块
from django.db import models
# 导入Django内置的用户模型
from django.contrib.auth.models import User
# 导入Django的最小值验证器
from django.core.validators import MinValueValidator
# 导入产品应用中的Product模型（假设products应用已注册）
from products.models import Product

class Cart(models.Model):
    """购物车主模型，每个用户对应唯一一个购物车"""
    # 定义与User模型的一对一关系字段
    # 一个用户只能有一个购物车
    user = models.OneToOneField(
        User,  # 关联的模型是User
        on_delete=models.CASCADE,  # 用户删除时级联删除购物车
        related_name='cart',  # 反向查询名称，可通过user.cart访问
        verbose_name='用户'  # 在管理后台显示的字段名
    )
    # 创建时间字段，自动记录购物车创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间字段，自动记录购物车最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        """模型的元数据配置"""
        # 在管理后台显示的单数名称
        verbose_name = '购物车'
        # 在管理后台显示的复数名称
        verbose_name_plural = '购物车'
        # 默认排序规则，按创建时间降序排列
        ordering = ['-created_at']
    
    def __str__(self):
        """返回模型的字符串表示，用于管理后台显示"""
        return f"{self.user.username}的购物车"
    
    def total_price(self):
        """计算购物车中所有商品的总金额"""
        # 遍历所有购物车项，计算每个购物车项的总价并求和
        return sum(item.total_price() for item in self.items.all())
    
    def item_count(self):
        """计算购物车中商品的总数量"""
        # 返回购物车项的数量统计
        return self.items.count()

class CartItem(models.Model):
    """购物车项模型，记录购物车中单个商品的信息"""
    # 定义与Cart模型的多对一关系字段
    # 一个购物车可以有多个购物车项
    cart = models.ForeignKey(
        Cart,  # 关联的模型是Cart
        on_delete=models.CASCADE,  # 购物车删除时级联删除所有项
        related_name='items',  # 反向查询名称，可通过cart.items访问
        verbose_name='购物车'  # 在管理后台显示的字段名
    )
    # 定义与Product模型的多对一关系字段
    # 一个商品可以出现在多个购物车项中
    product = models.ForeignKey(
        Product,  # 关联的模型是Product
        on_delete=models.CASCADE,  # 商品删除时级联删除购物车项
        verbose_name='商品'  # 在管理后台显示的字段名
    )
    # 商品数量字段，正整数类型
    quantity = models.PositiveIntegerField(
        '数量',  # 在管理后台显示的字段名
        default=1,  # 默认数量为1
        validators=[MinValueValidator(1)]  # 最小值为1的验证器
    )
    # 添加时间字段，自动记录商品添加到购物车的时间
    added_at = models.DateTimeField('添加时间', auto_now_add=True)
    
    class Meta:
        """模型的元数据配置"""
        # 在管理后台显示的单数名称
        verbose_name = '购物车项'
        # 在管理后台显示的复数名称
        verbose_name_plural = '购物车项'
        # 唯一性约束，确保同一购物车中同一商品只出现一次
        unique_together = ['cart', 'product']
        # 默认排序规则，按添加时间降序排列
        ordering = ['-added_at']
    
    def __str__(self):
        """返回模型的字符串表示，用于管理后台显示"""
        return f"{self.quantity} × {self.product.name}"
    
    def total_price(self):
        """计算当前购物车项的总价"""
        # 商品数量乘以商品单价
        return self.quantity * self.product.price