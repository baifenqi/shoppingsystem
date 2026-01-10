from django.contrib import admin
from django.db.models import Sum, Count
from .models import Order, OrderItem

# 订单项内联（订单详情页直接显示商品）
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # 不显示额外空行
    readonly_fields = ('product', 'price', 'quantity')  # 订单项商品/价格/数量只读（不允许修改）

# 订单管理（核心：统计、筛选、状态修改）
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """订单管理：聚焦统计和状态管理"""
    # 列表页显示核心字段
    list_display = ('id', 'user', 'full_name', 'total_price', 'status', 'created_at')
    # 可快速编辑的字段（订单状态）
    list_editable = ('status',)
    # 搜索字段（按用户/订单ID/手机号搜索）
    search_fields = ('id', 'user__username', 'full_name', 'phone', 'address')
    # 筛选条件（按状态/创建时间）
    list_filter = ('status', 'created_at')
    # 排序规则（按创建时间降序，最新订单在前）
    ordering = ('-created_at',)
    # 详情页显示订单项
    inlines = [OrderItemInline]
    # 只读字段（订单基础信息不允许修改）
    readonly_fields = ('user', 'total_price', 'created_at', 'updated_at')
    # 字段分组
    fieldsets = (
        ('订单信息', {
            'fields': ('user', 'total_price', 'status', 'created_at', 'updated_at')
        }),
        ('收货信息', {
            'fields': ('full_name', 'phone', 'address')
        }),
    )

    # 新增：订单统计（Admin首页显示核心数据）
    def changelist_view(self, request, extra_context=None):
        """重写列表页，添加订单统计数据"""
        extra_context = extra_context or {}
        
        # 1. 核心统计指标
        total_orders = Order.objects.count()  # 总订单数
        total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0  # 总销售额
        # 各状态订单数
        status_stats = Order.objects.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_stats}
        
        # 2. 传递到模板
        extra_context.update({
            'total_orders': total_orders,
            'total_sales': total_sales,
            'pending_orders': status_dict.get('pending', 0),  # 待付款
            'paid_orders': status_dict.get('paid', 0),        # 已付款
            'delivered_orders': status_dict.get('delivered', 0),  # 已发货
            'cancelled_orders': status_dict.get('cancelled', 0),  # 已取消
        })
        return super().changelist_view(request, extra_context)

# 订单项管理（仅查看，不开放编辑）
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order__status',)
    readonly_fields = ('order', 'product', 'price', 'quantity')
    # 禁止删除/添加订单项
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False