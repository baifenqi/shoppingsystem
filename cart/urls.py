from django.urls import path
from . import views

app_name = 'cart'  # 命名空间，和根URL的namespace='cart'匹配

urlpatterns = [
    # 购物车详情（核心，urls.py中引用的cart_detail）
    path('', views.cart_detail, name='cart_detail'),
    # 添加商品到购物车
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # 移除购物车商品
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # 更新商品数量
    path('update/<int:item_id>/', views.update_cart_quantity, name='update_quantity'),
    # 清空购物车
    path('clear/', views.clear_cart, name='clear_cart'),
]