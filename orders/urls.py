from django.urls import path
from . import views

app_name = 'orders'  # 命名空间（适配你的URL规范）

urlpatterns = [
    path('create/', views.create_order, name='create_order'),  # 创建订单
    path('list/', views.order_list, name='order_list'),        # 订单列表
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),  # 订单详情
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),  # 更新状态
]