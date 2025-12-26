# models.py
# 数据模型定义文件，定义购物车相关的数据库模型
# 导入Django模型模块
from django.db import models
# 导入Django内置的用户模型
from django.contrib.auth.models import User
# 导入Django的最小值验证器
from django.core.validators import MinValueValidator
# 导入Decimal用于金额精度控制（新增）
from decimal import Decimal
# 导入产品应用中的Product模型
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
        """
        计算购物车中所有商品的总金额（修改：添加异常防护+空值处理）
        :return: 总金额（Decimal类型，保证金额精度），空购物车返回Decimal('0.00')
        """
        total = Decimal('0.00')  # 初始化总金额为0，Decimal类型保证精度
        try:
            # 遍历所有购物车项，累加每个项的总价
            for item in self.items.all():
                item_total = item.total_price()
                # 确保item_total是Decimal类型，避免类型错误
                if isinstance(item_total, (int, float)):
                    item_total = Decimal(str(item_total))
                total += item_total
        except Exception as e:
            # 捕获异常（如商品价格为空），返回0避免页面崩溃
            print(f"计算购物车总金额出错：{e}")
            total = Decimal('0.00')
        return total
    
    # 新增别名方法，兼容阶段二的命名习惯（可选）
    def get_total_price(self):
        """别名方法，与阶段二教程中的命名一致，返回购物车总金额"""
        return self.total_price()
    
    def item_count(self):
        """
        计算购物车中商品的总件数（修改：修复逻辑错误，统计总数量而非商品种类数）
        :return: 所有商品的数量总和（int）
        """
        total_quantity = 0
        try:
            # 遍历所有购物车项，累加每个项的quantity
            for item in self.items.all():
                total_quantity += item.quantity
        except Exception as e:
            print(f"计算购物车商品总数出错：{e}")
            total_quantity = 0
        return total_quantity

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
        """
        计算当前购物车项的总价（修改：添加异常防护+精度保证）
        :return: 单个购物车项的总价（Decimal类型），出错返回Decimal('0.00')
        """
        try:
            # 确保price是Decimal类型（需Product的price字段为DecimalField）
            price = self.product.price
            if isinstance(price, (int, float)):
                price = Decimal(str(price))
            # 数量×单价，返回Decimal类型
            return self.quantity * price
        except Exception as e:
            # 捕获异常（如商品价格为空、数量非数字）
            print(f"计算购物车项总价出错：{e}")
            return Decimal('0.00')
    
    # 新增别名方法，兼容阶段二的命名习惯（可选）
    def get_subtotal(self):
        """别名方法，与阶段二教程中的命名一致，返回购物车项小计"""
        return self.total_price()