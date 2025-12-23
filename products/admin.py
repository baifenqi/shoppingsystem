# products/admin.py

from django.contrib import admin                #导入Django内置的管理后台框架
from django.utils.html import format_html       #导入HTML格式化工具
from .models import (                           #从models.py导入所有数据表模型
    Category, Product, ProductImage,            #Category- 商品分类,Product- 商品核心信息,ProductImage- 商品图片库
    Size, Color, Inventory,                     #Size和 Color- 规格属性,Inventory- 库存管理
    ProductAttribute, ProductAttributeValue     #ProductAttribute和 ProductAttributeValue- 商品属性系统
)


# ========== 内联模型（嵌套编辑关联数据） ==========
class ProductImageInline(admin.TabularInline):#以表格形式显示内联内容

    model = ProductImage#在商品编辑页中管理商品图片
    extra = 1 #默认显示1个空白表单
    verbose_name = "商品图片"
    verbose_name_plural = "商品图片列表"
    fields = ['image', 'alt_text', 'is_main', 'order']  #控制表单显示的字段顺序：
                                                        #image：图片上传字段
                                                        #alt_text：图片替代文本（SEO优化，图片无法显示时显示的文字）
                                                        #is_main：是否为主图（布尔值）
                                                        #order：排序序号
    
    readonly_fields = ['preview_image']  # 只读字段，preview_image字段只能查看，不能编辑用于显示图片预览缩略图


    def preview_image(self,obj): # 图片预览（自定义方法），obj：当前行的ProductImage对象，为每张图片生成预览
       
        """显示图片缩略图"""
        if obj.image:
            return format_html('<img src="{}" width="100" height="80" style="object-fit: cover;" />', obj.image.url)
            #安全生成HTML，防止XSS攻击，自动转义特殊字符，src="{}"：图片URL，用obj.image.url填充，width="100" height="80"：固定尺寸
            #style="object-fit: cover;"：CSS属性，保持比例填充
        return "暂无图片"
    preview_image.short_descreptiom = "图片预览"


class InventoryInline(admin.TabularInline):
    """库存SKU内联：在商品编辑页直接配置颜色/尺寸/库存"""

#SKU = Stock Keeping Unit（库存量单位）like:    商品：iPhone 15
#一个SKU代表一个具体的商品规格                  ├─ SKU1: 黑色，128G → 库存100台，价格5999
#不同颜色,尺寸,配置就是不同的SKU                ├─ SKU2: 黑色，256G → 库存50台，价格6999
#                                             └─ SKU3: 白色，256G → 库存30台，价格6999
    model = Inventory
    extra = 1
    verbose_name = "库存SKU"
    verbose_name_plural = "库存SKU列表"
    fields = [('color','size'),('count','price'),'sku','is_active']
    autocomplete_fields = ['color','size'] #搜索选择颜色/尺寸


class ProductAttributeValueInline(admin.TabularInline):
    """商品属性内联：在商品编辑页直接设置属性值"""

#EAV = Entity（实体）- Attribute（属性）- Value（值）
#这个内联让您可以在商品编辑页，动态地为商品添加任意属性和值（如材质、产地、规格等），
#支持属性搜索选择，实现灵活的商品属性管理。

    model = ProductAttributeValue
    extra = 1
    verbose_name = "商品属性值"
    verbose_name_plural = "商品属性值列表"
    autocomplete_fields  = ['attribute'] #搜索选择属性




# ========== 注册独立模型 ==========
@admin.register(Size)

class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'order']
    search_fields = ['name']
    ordering = ['order']
#size like:
#┌─────────┬──────┬──────┐
#│ 名称    │ 编码 │ 排序  │
#├─────────┼──────┼──────┤
#│ S码     │ S    │ 1    │
#│ M码     │ M    │ 2    │
#│ L码     │ L    │ 3    │
#│ XL码    │ XL   │ 4    │
#└─────────┴──────┴──────┘


@admin.register(Color)

class ColorAdmin(admin.ModelAdmin):
    list_display = ['name','code','color_preview','order']
    search_fields = ['name']
    ordering = ['order']

    def color_preview(self, obj):
        """显示颜色块预览"""
        if obj.code:
            return format_html('<div style="width:30px;height:30px;background:{};border:1px solid #ccc;"></div>', obj.code)
        return "无"
    
    color_preview.short_description = "颜色预览"

#颜色like:
#搜索... [搜索]      [添加颜色]
#┌─────────┬──────────┬──────────────┬──────┐
#│ 名称    │ 颜色代码 │ 颜色预览       │ 排序 │
#├─────────┼──────────┼──────────────┼──────┤
#│ 红色    │ #FF0000  │ █████████    │ 1    │
#│ 深蓝    │ #000080  │ █████████    │ 2    │
#│ 草绿    │ #7CFC00  │ █████████    │ 3    │
#│ 白色    │ #FFFFFF  │ █████████    │ 4    │
#│ 黑色    │ #000000  │ █████████    │ 5    │
#│ 灰色    │ #808080  │ █████████    │ 6    │
#└─────────┴──────────┴──────────────┴──────┘


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_required', 'order']
    search_fields = ['name']
    ordering = ['order']


#ProductAttribute表存储的是属性名定义like:
#┌─────┬──────────────┬──────────┬──────┐
#│ id  │ name         │ required │ order│
#├─────┼──────────────┼──────────┼──────┤
#│ 1   │ 材质         │ 是        │ 1    │
#│ 2   │ 产地         │ 是        │ 2    │
#│ 3   │ 屏幕尺寸     │ 是        │ 3    │
#│ 4   │ 处理器       │ 是        │ 4    │
#│ 5   │ 净含量       │ 是        │ 5    │
#│ 6   │ 适用季节     │ 否        │ 6    │
#│ 7   │ 风格         │ 否        │ 7    │
#└─────┴──────────────┴──────────┴──────┘    


# ========== 注册核心模型（商品+分类） ==========

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):                                          #name：分类名称
    list_display = ['name','parent','order','is_active','children_count']       #parent：父级分类（实现层级关系）
    list_filter = ['is_active','parent']                                        #order：同级分类的排序
    search_fields = ['name']                                                    #is_active：是否激活 ->上架or下架
    ordering = ['order']                                                        #children_count：子分类数量（自定义方法）
    autocomplete_fields = ['parent'] #搜索选择父分类

    def children_count(self, obj):
        """显示子级分类"""
        return obj.children.count()
    children_count.short_description = "子分类数"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock', 'status', 'is_featured']#name：商品名称 sku：商品编码（唯一标识）category：所属分类 price：价格 stock：库存总量status：商品状态（自定义属性）is_featured：是否推荐商品
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['name', 'sku']
    ordering = ['-created_at']
    readonly_fields = ['stock', 'view_count', 'sales_count', 'created_at', 'updated_at']#stock：由Inventory自动计算view_count：浏览数，由系统统计sales_count：销量，由订单系统更新 created_at/updated_at：自动时间戳

  #商品列表页
#┌─────────────────────────────────────────────────────────────────────────────────────┐
#│ 搜索商品... [搜索]      筛选：▼状态 ▼推荐商品 ▼分类     排序：▼最新创建              │
#├────┬──────────────┬──────────┬──────────────┬──────────┬────────┬────────┬─────────┤
#│ 名称│ SKU         │ 分类     │ 价格         │ 库存     │ 状态   │ 推荐   │ 操作    │
#├────┼──────────────┼──────────┼──────────┼──────────┼────────┼────────┼─────────┤
#│ iPhone│ IPH15_128G│ 手机     │ 5999.00     │ 156      │ 在售   │ ★      │ 编辑    │
#│ T恤  │ T001_WHITE │ 服装     │ 99.00       │ 0        │ 缺货   │        │ 编辑    │
#└────┴──────────────┴──────────┴──────────┴──────────┴────────┴────────┴─────────┘


    # 嵌套内联（商品编辑页直接管理图片/库存/属性）
    inlines = [ProductImageInline, InventoryInline, ProductAttributeValueInline]
    # 分栏显示字段，更清晰
    fieldsets = (
        ('基础信息', {
            'fields': (('name', 'sku'), ('slug', 'status'), 'is_featured')
        }),

        ('分类与描述', {
            'fields': ('category', 'short_description', 'description')
        }),

        ('价格与库存', {
            'fields': ('price', 'stock')  # stock由Inventory自动更新，设为只读
        }),

        ('统计信息', {
            'fields': ('view_count', 'sales_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)  # 可折叠
        }),
    )
    autocomplete_fields = ['category']  # 搜索选择分类




#完整效果：

"""
════════════════════

■ 基础信息
名称:   [iPhone 15          ]     SKU:    [IPH15_128G       ]
Slug:  [iphone-15         ]     状态:    [在售            ]
推荐商品: [✓ 设为推荐商品     ]

■ 分类与描述
分类:   [手机              ▼]
简短描述: [最新款iPhone...     ]
详细描述: [<富文本编辑器>      ]

■ 价格与库存
价格:   [5999.00           ]
库存:   [156               ] ← 只读,由库存SKU自动计算

■ 统计信息 ▼（点击展开）
浏览数:  [1245             ]
销量:   [89               ]
创建时间:[2024-01-15 10:30 ]
更新时间:[2024-01-20 14:15 ]

════════════════════
以下为内联管理部分
════════════════════   """
  