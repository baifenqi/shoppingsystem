from django.db import models


class Category(models.Model):
    """商品分类模型，用于对商品进行一级分类"""
    cname = models.CharField(max_length=10, verbose_name='分类名称')
    
    def __str__(self):
        return f'Category:{self.cname}'
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name


class Goods(models.Model):
    """商品核心信息模型，存储商品的基本信息"""
    gname = models.CharField(max_length=100, verbose_name='商品名称')
    gdesc = models.CharField(max_length=100, verbose_name='商品描述')
    oldprice = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='原价')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='现价')
    # 关联分类：一个分类下可以有多个商品，商品删除时不影响分类
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='所属分类')
    
    def __str__(self):
        return f'Goods:{self.gname}'
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class GoodsDetaiName(models.Model):
    """
    商品详情属性名称模型
    用于定义商品详情中的属性名称，如"材质"、"产地"等
    注意：类名可能有拼写错误，应为GoodsDetailName
    """
    gname = models.CharField(max_length=30, verbose_name='属性名称')
    
    def __str__(self):
        return f'GoodsDetailName:{self.gname}'
    
    class Meta:
        verbose_name = '商品详情属性名'
        verbose_name_plural = verbose_name


class GoodsDetail(models.Model):
    """
    商品详情模型
    存储商品的具体属性值，当前设计使用图片存储属性值
    注意：gdurl字段为ImageField，可能更适合存储属性图片而非文本属性值
    """
    gdurl = models.ImageField(upload_to='goods_details/', verbose_name='属性图片')
    # 关联属性名称：一个属性名可以对应多个商品的属性值
    gdname = models.ForeignKey(GoodsDetaiName, on_delete=models.CASCADE, verbose_name='属性名称')
    # 关联商品：一个商品可以有多个详情属性
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='所属商品')
    
    def __str__(self):
        return f'GoodsDetail:{self.id}'
    
    class Meta:
        verbose_name = '商品详情'
        verbose_name_plural = verbose_name


class Size(models.Model):
    """商品尺寸规格模型"""
    sname = models.CharField(max_length=10, verbose_name='尺寸名称')
    
    def __str__(self):
        return f'Size:{self.sname}'
    
    class Meta:
        verbose_name = '商品尺寸'
        verbose_name_plural = verbose_name


class Color(models.Model):
    """商品颜色规格模型"""
    colorname = models.CharField(max_length=10, verbose_name='颜色名称')
    colorurl = models.ImageField(upload_to='color/', verbose_name='颜色图片')
    
    def __str__(self):
        return f'Color:{self.colorname}'
    
    class Meta:
        verbose_name = '商品颜色'
        verbose_name_plural = verbose_name


class Inventory(models.Model):
    """
    商品库存模型（SKU模型）
    通过商品、颜色、尺寸的唯一组合确定一个单品SKU
    记录每个SKU的库存数量
    """
    count = models.PositiveIntegerField(verbose_name='库存数量')
    # 关联颜色：一个颜色可以有多个库存记录
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name='颜色')
    # 关联商品：一个商品可以有多个库存记录（不同颜色尺寸）
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    # 关联尺寸：一个尺寸可以有多个库存记录
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name='尺寸')
    
    def __str__(self):
        return f'Inventory:{self.id}'
    
    class Meta:
        verbose_name = '商品库存'
        verbose_name_plural = verbose_name
        # 建议添加唯一约束，确保同一商品的同一颜色尺寸组合唯一
        unique_together = ['goods', 'color', 'size']