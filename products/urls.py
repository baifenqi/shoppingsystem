# products/urls.py
from django.urls import path
from . import views

app_name = 'products'  # 应用命名空间，避免URL重名

urlpatterns = [
    # 首页视图（函数视图，直接映射）
    path('', views.home, name='home'),
    
    # 商品列表页（类视图，需调用as_view()方法）
    path('products/', views.ProductListView.as_view(), name='product_list'),
    # 分类筛选商品列表（复用商品列表类视图，通过URL参数传递分类ID）
    path('category/<int:category_id>/', views.ProductListView.as_view(), name='product_list_by_category'),
    
    # 商品详情页（类视图，匹配商品ID）
    path('product/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # 分类列表页
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    
    # 商品详情页添加到购物车
    path('product/<int:product_id>/add-to-cart/', views.add_to_cart_from_detail, name='add_to_cart_from_detail'),
    
    # 获取库存数据（AJAX接口）
    path('product/<int:product_id>/inventory/', views.get_inventory_data, name='get_inventory_data'),
    
    # 快速添加到购物车（AJAX接口）
    path('product/<int:product_id>/quick-add/', views.quick_add_to_cart, name='quick_add_to_cart'),
    
    # 推荐商品
    path('featured/', views.FeaturedProductsView.as_view(), name='featured_products'),
    
    # 新品上架
    path('new-arrivals/', views.NewArrivalsView.as_view(), name='new_arrivals'),
    
    # 特价商品
    path('sale/', views.SaleProductsView.as_view(), name='sale_products'),
    
    # 搜索建议（AJAX接口）
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]