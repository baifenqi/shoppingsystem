# urls.py
# 购物车应用的URL路由配置文件，定义URL模式与视图函数的映射关系
from django.urls import path
from . import views

# 应用命名空间，用于URL反向解析时区分不同应用的同名URL
app_name = 'cart'

# URL模式列表，Django会按照顺序匹配这些模式
urlpatterns = [
    # 购物车详情页面URL
    # 空路径映射到cart_detail视图函数
    # name='cart_detail'用于模板中URL反向解析
    path('', views.cart_detail, name='cart_detail'),
    
    # 添加商品到购物车URL
    # <int:product_id>捕获商品ID作为整数参数传递给视图函数
    # 商品详情页的"加入购物车"按钮通常指向此URL
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # 从购物车移除商品URL
    # <int:item_id>捕获购物车项ID作为整数参数
    # 购物车页面每个商品的"删除"按钮指向此URL
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # 更新购物车商品数量URL（支持AJAX）
    # 用于购物车页面中修改商品数量的异步请求
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    
    # 清空购物车URL
    # 购物车页面的"清空购物车"按钮指向此URL
    path('clear/', views.clear_cart, name='clear_cart'),
    
    # 结算页面URL
    # 购物车页面的"去结算"按钮指向此URL
    # path('checkout/', views.checkout, name='checkout'),  # 暂未实现，保持注释
    
    # 确认订单URL（暂未实现，注释掉避免报错，后续实现视图后再启用）
    # path('confirm-order/', views.confirm_order, name='confirm_order'),
]

# 注意：此文件需要被项目的根URL配置（通常是项目的urls.py）包含
# 示例包含方式：path('cart/', include('cart.urls')),