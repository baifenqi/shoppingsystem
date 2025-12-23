# products/urls.py
from django.urls import path
from . import views

app_name = 'products'  # 应用命名空间，避免URL重名

urlpatterns = [
    # 商品列表页（首页）：支持按分类筛选
    path('', views.product_list, name='product_list'),
    path('category/<<int:category_id>/', views.product_list, name='product_list_by_category'),
    # 商品详情页：按商品ID访问
    path('product/<<int:product_id>/', views.product_detail, name='product_detail'),
]