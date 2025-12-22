# products/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import os


class Category(models.Model):
    """商品分类模型"""
    name = models.CharField('分类名称', max_length=50, unique=True)  # 修改字段名为name
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name='父级分类',
        related_name='children'
    )
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否激活', default=True)
    
    def __str__(self):
        return self.name  # 修改这里
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']
        db_table = 'products_category'  # 修改表名前缀


class Product(models.Model):  # 修改类名为Product
    """商品核心信息模型"""
    
    # 商品状态选项
    PRODUCT_STATUS = (
        ('draft', '草稿'),
        ('published', '已上架'),
        ('out_of_stock', '缺货'),
        ('discontinued', '已下架'),
    )
    
    name = models.CharField('商品名称', max_length=200, db_index=True)  # 修改字段名为name
    slug = models.SlugField('URL标识', max_length=200, unique=True, blank=True, null=True)
    description = models.TextField('商品描述', blank=True)  # 修改字段名为description
    short_description = models.CharField('商品简述', max_length=200, blank=True)
    sku = models.CharField('商品编码', max_length=50, unique=True, db_index=True)
    
    # 价格字段
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, default=0)
    
    # 商品信息
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='所属分类',
        related_name='products'
    )
    
    # 库存字段
    stock = models.PositiveIntegerField('总库存', default=0)
    
    # 商品状态
    status = models.CharField('商品状态', max_length=20, choices=PRODUCT_STATUS, default='draft')
    is_featured = models.BooleanField('推荐商品', default=False)
    
    # 时间字段
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    # 统计字段
    view_count = models.PositiveIntegerField('浏览量', default=0)
    sales_count = models.PositiveIntegerField('销量', default=0)
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['price', 'status']),
            models.Index(fields=['category', 'status']),
        ]
        db_table = 'products_product'  # 修改表名前缀
    
    def __str__(self):
        return f'{self.name} ({self.sku})'
    
    def is_available(self):
        """检查商品是否可售"""
        return self.status == 'published' and self.stock > 0
    
    def decrease_stock(self, quantity):
        """减少库存"""
        if quantity > self.stock:
            return False
        self.stock -= quantity
        self.save()
        return True
    
    def increase_stock(self, quantity):
        """增加库存"""
        self.stock += quantity
        self.save()
        return True


class ProductImage(models.Model):  # 修改类名
    """商品图片模型"""
    product = models.ForeignKey(  # 修改字段名
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='images'
    )
    image = models.ImageField('图片', upload_to='products/%Y/%m/%d/')  # 修改上传路径
    alt_text = models.CharField('图片说明', max_length=200, blank=True)
    is_main = models.BooleanField('主图', default=False)
    order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name
        ordering = ['order', '-is_main', 'id']
        db_table = 'products_productimage'  # 修改表名前缀
    
    def __str__(self):
        return f'{self.product.name} - 图片{self.id}'


class Size(models.Model):
    """商品尺寸规格模型"""
    name = models.CharField('尺寸名称', max_length=20, unique=True)  # 修改字段名
    code = models.CharField('尺寸代码', max_length=10, blank=True)
    description = models.CharField('尺寸描述', max_length=100, blank=True)
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '商品尺寸'
        verbose_name_plural = verbose_name
        ordering = ['order']
        db_table = 'products_size'  # 修改表名前缀
    
    def __str__(self):
        return f'{self.name}'


class Color(models.Model):
    """商品颜色规格模型"""
    name = models.CharField('颜色名称', max_length=20, unique=True)  # 修改字段名
    code = models.CharField('颜色代码', max_length=7, help_text='十六进制颜色代码，如#FF0000', blank=True)
    image = models.ImageField('颜色图片', upload_to='colors/', blank=True, null=True)  # 修改字段名
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '商品颜色'
        verbose_name_plural = verbose_name
        ordering = ['order']
        db_table = 'products_color'  # 修改表名前缀
    
    def __str__(self):
        return f'{self.name}'


class Inventory(models.Model):
    """商品库存模型（SKU模型）"""
    product = models.ForeignKey(  # 修改字段名
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='inventory_items'
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        verbose_name='颜色',
        null=True,
        blank=True
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        verbose_name='尺寸',
        null=True,
        blank=True
    )
    
    # 库存和价格
    count = models.PositiveIntegerField('库存数量', default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # SKU信息
    sku = models.CharField('SKU编码', max_length=50, unique=True, db_index=True)
    barcode = models.CharField('条形码', max_length=50, blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '商品库存'
        verbose_name_plural = verbose_name
        unique_together = ['product', 'color', 'size']
        ordering = ['product', 'color', 'size']
        db_table = 'products_inventory'  # 修改表名前缀
    
    def __str__(self):
        parts = [self.product.name]
        if self.color:
            parts.append(self.color.name)
        if self.size:
            parts.append(self.size.name)
        return f"{' '.join(parts)} (库存: {self.count})"
    
    def get_price(self):
        """获取价格"""
        if self.price is not None:
            return self.price
        return self.product.price
    
    def is_in_stock(self):
        """检查是否有库存"""
        return self.count > 0


class ProductAttribute(models.Model):
    """商品属性名称模型"""
    name = models.CharField('属性名称', max_length=50, unique=True)
    is_required = models.BooleanField('是否必填', default=False)
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '商品属性'
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']
        db_table = 'products_productattribute'
    
    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """商品属性值模型"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='attributes'
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        verbose_name='属性'
    )
    value = models.CharField('属性值', max_length=200)
    
    class Meta:
        verbose_name = '商品属性值'
        verbose_name_plural = verbose_name
        unique_together = ['product', 'attribute']
        db_table = 'products_productattributevalue'
    
    def __str__(self):
        return f'{self.product.name} - {self.attribute.name}: {self.value}'


# 信号处理
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver([post_save, post_delete], sender=Inventory)
def update_product_stock(sender, instance, **kwargs):
    """当Inventory发生变化时，更新对应的商品总库存"""
    product = instance.product
    total_stock = product.inventory_items.aggregate(
        total=models.Sum('count')
    )['total'] or 0
    product.stock = total_stock
    product.save(update_fields=['stock'])