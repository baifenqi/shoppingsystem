# products/models.py
"""
商品应用数据模型定义文件
本文件定义了电商系统的所有核心数据模型，包括商品、分类、库存、属性等实体
所有模型都继承自Django的models.Model基类，用于自动创建数据库表和字段
模型关系设计遵循数据库规范化原则，确保数据一致性和查询效率
"""

# 导入Django核心模块
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import os


class Category(models.Model):
    """
    商品分类模型
    用于对商品进行层级分类管理，支持无限级分类结构
    
    字段说明：
    - name: 分类名称，必须唯一，用于前台展示和后台管理
    - parent: 父级分类自关联字段，实现多级分类，可为空表示顶级分类
    - order: 排序字段，控制分类在前台的显示顺序，数值越小显示越靠前
    - is_active: 激活状态字段，控制分类是否在前台显示
    
    关联关系：
    - 一个分类可以有多个子分类（通过children反向关联）
    - 一个分类可以有多个商品（通过products反向关联）
    """
    
    # 分类名称字段，最大长度50字符，必须唯一，用于后台显示和管理
    name = models.CharField('分类名称', max_length=50, unique=True)
    
    # 父级分类自关联字段，实现多级分类结构
    # on_delete=CASCADE表示父分类删除时子分类也删除
    # null=True, blank=True表示顶级分类可以为空
    # related_name='children'用于反向查询子分类
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name='父级分类',
        related_name='children'
    )
    
    # 排序字段，用于控制分类在前台的显示顺序，数值越小显示越靠前
    order = models.IntegerField('排序', default=0)
    
    # 激活状态字段，控制分类是否在前台显示，默认激活
    is_active = models.BooleanField('是否激活', default=True)
    
    def __str__(self):
        """
        模型对象的字符串表示方法
        在Django管理后台、shell等地方显示的名称
        返回：分类名称
        """
        return self.name
    
    class Meta:
        """
        模型的元数据配置
        用于定义模型的数据库表名、后台显示名称、排序规则等
        """
        # 在Django管理后台显示的单数名称
        verbose_name = '商品分类'
        # 在Django管理后台显示的复数名称
        verbose_name_plural = verbose_name
        # 默认排序规则，先按order升序，再按id升序
        ordering = ['order', 'id']
        # 数据库表名，使用应用名_模型名格式
        db_table = 'products_category'


class Product(models.Model):
    """
    商品核心信息模型
    存储商品的基本信息，是电商系统的核心实体
    一个商品可以有多个SKU（通过Inventory模型管理）
    
    字段说明：
    - name: 商品名称，建立索引以提高搜索性能
    - slug: URL标识字段，用于生成SEO友好的商品详情页URL
    - description: 商品详细描述，支持长文本
    - short_description: 商品简短描述，用于列表页展示
    - sku: 商品唯一编码，用于库存管理和物流
    - price: 商品销售价格，使用DecimalField确保精度
    - category: 商品所属分类，多对一关系
    - stock: 商品总库存，汇总所有SKU的库存数量
    - status: 商品状态，从预定义选项中选择
    - is_featured: 是否推荐商品，用于首页展示
    - created_at: 商品创建时间，自动设置
    - updated_at: 商品最后更新时间，自动更新
    - view_count: 商品浏览量，记录访问次数
    - sales_count: 商品销量，记录购买数量
    """
    
    # 商品状态选项定义
    # 用于限制status字段的取值范围，同时在前台显示中文
    PRODUCT_STATUS = (
        ('draft', '草稿'),          # 商品已创建但未上架
        ('published', '已上架'),     # 商品已上架可销售
        ('out_of_stock', '缺货'),    # 商品暂时缺货
        ('discontinued', '已下架'),  # 商品已永久下架
    )
    
    # 商品名称字段，建立索引以提高搜索性能
    name = models.CharField('商品名称', max_length=200, db_index=True)
    
    # URL标识字段，用于生成SEO友好的商品详情页URL
    # 示例：iphone-13-pro-max
    slug = models.SlugField('URL标识', max_length=200, unique=True, blank=True, null=True)
    
    # 商品详细描述，使用TextField支持长文本
    description = models.TextField('商品描述', blank=True)
    
    # 商品简短描述，用于列表页展示
    short_description = models.CharField('商品简述', max_length=200, blank=True)
    
    # 商品唯一编码，用于库存管理和物流
    sku = models.CharField('商品编码', max_length=50, unique=True, db_index=True)
    
    # 商品销售价格，使用DecimalField确保精度
    # max_digits=10表示最多10位数字（包括小数位）
    # decimal_places=2表示保留2位小数
    price = models.DecimalField(
        '商品单价',
        max_digits=10,  # 最大位数（含小数）
        decimal_places=2,  # 小数点后2位
        validators=[MinValueValidator(Decimal('0.01'))]  # 最低价格0.01元
    )
    
    # 商品所属分类，多对一关系
    # on_delete=SET_NULL表示分类删除时商品不删除，分类字段设为NULL
    # null=True, blank=True允许商品没有分类
    # related_name='products'用于从分类反向查询商品
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='所属分类',
        related_name='products'
    )
    
    # 商品总库存，汇总所有SKU的库存数量
    stock = models.PositiveIntegerField('总库存', default=0)
    
    # 商品状态，从PRODUCT_STATUS中选择
    status = models.CharField('商品状态', max_length=20, choices=PRODUCT_STATUS, default='draft')
    
    # 是否推荐商品，用于首页展示等场景
    is_featured = models.BooleanField('推荐商品', default=False)
    
    # 商品创建时间，auto_now_add=True表示创建时自动设置当前时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    # 商品最后更新时间，auto_now=True表示每次保存时自动更新
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    # 商品浏览量，记录商品详情页被访问的次数
    view_count = models.PositiveIntegerField('浏览量', default=0)
    
    # 商品销量，记录商品被购买的总数量
    sales_count = models.PositiveIntegerField('销量', default=0)
    
    class Meta:
        """
        商品的元数据配置
        """
        # 后台显示名称
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        
        # 默认按创建时间降序排列，新商品显示在前面
        ordering = ['-created_at']
        
        # 数据库索引配置，提高查询性能
        indexes = [
            # 复合索引：按价格和状态查询
            models.Index(fields=['price', 'status']),
            # 复合索引：按分类和状态查询
            models.Index(fields=['category', 'status']),
        ]
        
        # 数据库表名
        db_table = 'products_product'
    
    def __str__(self):
        """
        返回商品的字符串表示
        格式：商品名称 (商品编码)
        示例：iPhone 13 Pro Max (IPHONE13PM256)
        """
        return f'{self.name} ({self.sku})'
    
    def is_available(self):
        """
        检查商品是否可售
        可售条件：状态为已上架且库存大于0
        返回：布尔值，True表示可售，False表示不可售
        """
        return self.status == 'published' and self.stock > 0
    
    def decrease_stock(self, quantity):
        """
        减少商品库存
        通常在用户下单成功时调用
        
        参数：
            quantity: 要减少的数量，正整数
            
        返回：
            布尔值，True表示减少成功，False表示库存不足
        """
        if quantity > self.stock:
            return False
        self.stock -= quantity
        self.save()
        return True
    
    def increase_stock(self, quantity):
        """
        增加商品库存
        通常在补货、退货等场景调用
        
        参数：
            quantity: 要增加的数量，正整数
            
        返回：
            布尔值，True表示增加成功
        """
        self.stock += quantity
        self.save()
        return True


class ProductImage(models.Model):
    """
    商品图片模型
    一个商品可以有多个图片，支持主图设置
    
    字段说明：
    - product: 关联的商品，多对一关系
    - image: 图片文件字段，按年月日自动组织上传路径
    - alt_text: 图片替代文本，用于SEO和无障碍访问
    - is_main: 是否为主图，一个商品只能有一个主图
    - order: 图片排序，用于控制多图的显示顺序
    - created_at: 图片上传时间
    """
    
    # 关联的商品，多对一关系
    # on_delete=CASCADE表示商品删除时图片也删除
    # related_name='images'用于从商品反向查询图片
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='images'
    )
    
    # 图片文件字段
    # upload_to指定上传路径，按年月日自动组织
    image = models.ImageField('图片', upload_to='products/%Y/%m/%d/')
    
    # 图片替代文本，用于SEO和无障碍访问
    alt_text = models.CharField('图片说明', max_length=200, blank=True)
    
    # 是否为主图，一个商品只能有一个主图
    is_main = models.BooleanField('主图', default=False)
    
    # 图片排序，用于控制多图的显示顺序
    order = models.IntegerField('排序', default=0)
    
    # 图片上传时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        """商品图片的元数据配置"""
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name
        
        # 排序规则：先按order升序，再按主图降序，最后按id升序
        ordering = ['order', '-is_main', 'id']
        
        db_table = 'products_productimage'
    
    def __str__(self):
        """
        返回商品图片的字符串表示
        格式：商品名称 - 图片ID
        示例：iPhone 13 Pro Max - 图片1
        """
        return f'{self.product.name} - 图片{self.id}'


class Size(models.Model):
    """
    商品尺寸规格模型
    用于管理商品的尺寸规格，如服装尺码、鞋码等
    
    字段说明：
    - name: 尺寸名称，必须唯一
    - code: 尺寸代码，用于内部识别或外部系统对接
    - description: 尺寸描述，如尺寸对应的具体测量值
    - order: 排序字段
    """
    
    # 尺寸名称，必须唯一
    name = models.CharField('尺寸名称', max_length=20, unique=True)
    
    # 尺寸代码，用于内部识别或外部系统对接
    code = models.CharField('尺寸代码', max_length=10, blank=True)
    
    # 尺寸描述，如尺寸对应的具体测量值
    description = models.CharField('尺寸描述', max_length=100, blank=True)
    
    # 排序字段
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        """尺寸的元数据配置"""
        verbose_name = '商品尺寸'
        verbose_name_plural = verbose_name
        
        # 按order升序排列
        ordering = ['order']
        
        db_table = 'products_size'
    
    def __str__(self):
        """
        返回尺寸的字符串表示
        返回：尺寸名称
        示例：M
        """
        return f'{self.name}'


class Color(models.Model):
    """
    商品颜色规格模型
    用于管理商品的颜色规格
    
    字段说明：
    - name: 颜色名称，必须唯一
    - code: 十六进制颜色代码，用于前台显示
    - image: 颜色图片，用于展示颜色效果
    - order: 排序字段
    """
    
    # 颜色名称，必须唯一
    name = models.CharField('颜色名称', max_length=20, unique=True)
    
    # 十六进制颜色代码，用于前台显示
    # 示例：#FF0000 表示红色
    code = models.CharField('颜色代码', max_length=7, help_text='十六进制颜色代码，如#FF0000', blank=True)
    
    # 颜色图片，用于展示颜色效果
    image = models.ImageField('颜色图片', upload_to='colors/', blank=True, null=True)
    
    # 排序字段
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        """颜色的元数据配置"""
        verbose_name = '商品颜色'
        verbose_name_plural = verbose_name
        
        # 按order升序排列
        ordering = ['order']
        
        db_table = 'products_color'
    
    def __str__(self):
        """
        返回颜色的字符串表示
        返回：颜色名称
        示例：红色
        """
        return f'{self.name}'


class Inventory(models.Model):
    """
    商品库存模型（SKU模型）
    通过商品、颜色、尺寸的唯一组合确定一个单品SKU
    SKU = Stock Keeping Unit，库存最小单位
    
    字段说明：
    - product: 关联的商品
    - color: 关联的颜色，可以为空（对于没有颜色规格的商品）
    - size: 关联的尺寸，可以为空（对于没有尺寸规格的商品）
    - count: 库存数量，必须大于等于0
    - price: SKU特定价格，如果为空则使用商品的基础价格
    - sku: SKU编码，库存最小单位的唯一标识
    - barcode: 条形码，用于物流和零售
    - is_active: SKU是否激活，可以临时禁用某个SKU
    - created_at: 创建时间
    - updated_at: 最后更新时间
    """
    
    # 关联的商品
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='inventory_items'
    )
    
    # 关联的颜色，可以为空（对于没有颜色规格的商品）
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        verbose_name='颜色',
        null=True,
        blank=True
    )
    
    # 关联的尺寸，可以为空（对于没有尺寸规格的商品）
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        verbose_name='尺寸',
        null=True,
        blank=True
    )
    
    # 库存数量，必须大于等于0
    count = models.PositiveIntegerField('库存数量', default=0, validators=[MinValueValidator(0)])
    
    # SKU特定价格，如果为空则使用商品的基础价格
    # 允许某些SKU有特殊定价
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # SKU编码，库存最小单位的唯一标识
    sku = models.CharField('SKU编码', max_length=50, unique=True, db_index=True)
    
    # 条形码，用于物流和零售
    barcode = models.CharField('条形码', max_length=50, blank=True)
    
    # SKU是否激活，可以临时禁用某个SKU
    is_active = models.BooleanField('是否激活', default=True)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    # 最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        """库存的元数据配置"""
        verbose_name = '商品库存'
        verbose_name_plural = verbose_name
        
        # 唯一约束：确保同一商品的同一颜色尺寸组合唯一
        unique_together = ['product', 'color', 'size']
        
        # 排序规则：先按商品，再按颜色，最后按尺寸
        ordering = ['product', 'color', 'size']
        
        db_table = 'products_inventory'
    
    def __str__(self):
        """
        返回库存的字符串表示
        格式：商品名称 颜色名称 尺寸名称 (库存: 数量)
        示例：iPhone 13 Pro Max 蓝色 256GB (库存: 100)
        """
        parts = [self.product.name]
        if self.color:
            parts.append(self.color.name)
        if self.size:
            parts.append(self.size.name)
        return f"{' '.join(parts)} (库存: {self.count})"
    
    def get_price(self):
        """
        获取SKU的实际价格
        优先使用SKU特定价格，如果没有则使用商品基础价格
        
        返回：
            Decimal对象，商品价格
        """
        if self.price is not None:
            return self.price
        return self.product.price
    
    def is_in_stock(self):
        """
        检查SKU是否有库存
        
        返回：
            布尔值，True表示有库存
        """
        return self.count > 0


class ProductAttribute(models.Model):
    """
    商品属性名称模型
    定义商品的各种属性，如材质、产地、重量等
    
    字段说明：
    - name: 属性名称，必须唯一
    - is_required: 是否必填属性，控制在前台是否必须填写
    - order: 排序字段
    """
    
    # 属性名称，必须唯一
    name = models.CharField('属性名称', max_length=50, unique=True)
    
    # 是否必填属性，控制在前台是否必须填写
    is_required = models.BooleanField('是否必填', default=False)
    
    # 排序字段
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        """属性名称的元数据配置"""
        verbose_name = '商品属性'
        verbose_name_plural = verbose_name
        
        # 先按order升序，再按id升序
        ordering = ['order', 'id']
        
        db_table = 'products_productattribute'
    
    def __str__(self):
        """
        返回属性名称的字符串表示
        返回：属性名称
        示例：材质
        """
        return self.name


class ProductAttributeValue(models.Model):
    """
    商品属性值模型
    存储商品的具体属性值
    
    字段说明：
    - product: 关联的商品
    - attribute: 关联的属性名称
    - value: 属性值
    """
    
    # 关联的商品
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='attributes'
    )
    
    # 关联的属性名称
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        verbose_name='属性'
    )
    
    # 属性值
    value = models.CharField('属性值', max_length=200)
    
    class Meta:
        """属性值的元数据配置"""
        verbose_name = '商品属性值'
        verbose_name_plural = verbose_name
        
        # 唯一约束：确保同一个商品的同一个属性只有一个值
        unique_together = ['product', 'attribute']
        
        db_table = 'products_productattributevalue'
    
    def __str__(self):
        """
        返回属性值的字符串表示
        格式：商品名称 - 属性名称: 属性值
        示例：iPhone 13 Pro Max - 颜色: 深空灰
        """
        return f'{self.product.name} - {self.attribute.name}: {self.value}'


# 信号处理模块
# 用于在模型保存、删除等操作前后执行特定逻辑
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver([post_save, post_delete], sender=Inventory)
def update_product_stock(sender, instance, **kwargs):
    """
    库存信号处理器
    当Inventory模型实例保存或删除时，自动更新对应商品的总库存
    
    功能：保持Product.stock与Inventory.count总和的一致性
    触发时机：Inventory创建、更新、删除时
    避免手动管理库存时可能出现的数据不一致问题
    
    参数：
        sender: 发送信号的模型类
        instance: 触发信号的模型实例
        **kwargs: 其他信号参数
    
    处理流程：
        1. 获取关联的商品
        2. 统计该商品所有SKU的库存总和
        3. 更新商品的stock字段
        4. 只更新stock字段，避免触发其他信号
    
    设计目的：
        实现库存数据的自动同步，确保商品总库存始终准确
    """
    # 获取关联的商品
    product = instance.product
    
    # 聚合计算：统计该商品所有SKU的库存总和
    # 如果没有任何库存，则total为0
    total_stock = product.inventory_items.aggregate(
        total=models.Sum('count')
    )['total'] or 0
    
    # 更新商品的总库存
    product.stock = total_stock
    
    # 只更新stock字段，避免触发其他信号的循环调用
    product.save(update_fields=['stock'])