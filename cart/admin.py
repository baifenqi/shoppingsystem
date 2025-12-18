# admin.py
# Django后台管理配置文件，定义模型在Django管理后台的显示和编辑方式
# 导入Django管理模块
from django.contrib import admin
# 导入当前应用的模型
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    """购物车项内联类，允许在购物车编辑页面直接管理购物车项"""
    # 指定内联关联的模型为CartItem
    model = CartItem
    # 设置额外显示的表单数量为0，只显示已有项目
    extra = 0
    # 设置added_at字段为只读，防止在后台修改
    readonly_fields = ['added_at']
    # 设置product字段使用搜索框选择，提高选择效率
    raw_id_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """购物车模型的后台管理配置类"""
    # 在列表页显示的字段，包括用户、商品数量、总价和创建时间
    list_display = ['user', 'item_count', 'total_price', 'created_at']
    # 在列表页右侧提供的筛选器，可按创建时间和更新时间筛选
    list_filter = ['created_at', 'updated_at']
    # 在列表页顶部提供的搜索框，可按用户名和邮箱搜索
    search_fields = ['user__username', 'user__email']
    # 设置内联显示的模型，可以在购物车页面直接编辑购物车项
    inlines = [CartItemInline]
    # 设置创建时间和更新时间为只读字段，不允许修改
    readonly_fields = ['created_at', 'updated_at']
    # 在列表页添加日期层次导航，方便按日期筛选
    date_hierarchy = 'created_at'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """购物车项模型的后台管理配置类"""
    # 在列表页显示的字段，包括购物车、商品、数量、小计和添加时间
    list_display = ['cart', 'product', 'quantity', 'item_total_price', 'added_at']
    # 在列表页右侧提供的筛选器，可按添加时间和商品分类筛选
    list_filter = ['added_at', 'product__category']
    # 在列表页顶部提供的搜索框，可按商品名称和用户名搜索
    search_fields = ['product__name', 'cart__user__username']
    # 设置购物车和商品字段使用搜索框选择，提高选择效率
    raw_id_fields = ['cart', 'product']
    # 设置添加时间为只读字段，不允许修改
    readonly_fields = ['added_at']
    # 设置每页显示20条记录，便于查看和管理
    list_per_page = 20
    
    def item_total_price(self, obj):
        """自定义列表页显示列，计算并返回购物车项的小计金额"""
        # 调用CartItem模型的total_price方法计算小计金额
        return obj.total_price()
    # 设置自定义列在管理后台的显示名称
    item_total_price.short_description = '小计金额'