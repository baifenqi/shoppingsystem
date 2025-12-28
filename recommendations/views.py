"""
推荐视图
提供推荐商品API接口
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .algorithms import SimpleRecommender
from products.models import Product
import json

@require_GET
@cache_page(60 * 5)  # 缓存5分钟
def get_recommendations(request):
    """
    获取推荐商品API接口
    
    支持参数：
    - type: 推荐类型 (cart, hot, new, featured, related)
    - product_id: 当type=related时需要的商品ID
    - limit: 返回商品数量，默认6
    - format: 返回格式，支持json和html
    
    :param request: HTTP请求对象
    :return: JSON响应或HTML片段
    """
    # 获取请求参数
    rec_type = request.GET.get('type', 'cart')
    product_id = request.GET.get('product_id')
    limit = int(request.GET.get('limit', 6))
    response_format = request.GET.get('format', 'json')
    
    # 初始化推荐器
    recommender = SimpleRecommender(request.user if request.user.is_authenticated else None)
    
    # 根据类型选择推荐策略
    if rec_type == 'hot':
        recommendations = recommender.recommend_hot_products(limit)
    elif rec_type == 'new':
        recommendations = recommender.recommend_new_products(limit)
    elif rec_type == 'featured':
        recommendations = recommender.recommend_featured_products(limit)
    elif rec_type == 'related' and product_id:
        try:
            product = Product.objects.get(id=product_id, status='published')
            recommendations = recommender.recommend_related_products(product, limit)
        except Product.DoesNotExist:
            recommendations = recommender.recommend_hot_products(limit)
    else:  # 默认：基于购物车/用户的推荐
        recommendations = recommender.recommend_for_user(limit)
    
    # 准备商品数据
    products_data = []
    for product in recommendations:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'image': product.images.filter(is_main=True).first().image.url if product.images.filter(is_main=True).exists() else None,
            'url': f'/products/{product.id}/',
            'category': product.category.name if product.category else '未分类',
        })
    
    # 根据格式返回响应
    if response_format == 'html' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 返回HTML片段用于异步加载
        context = {'recommendations': recommendations[:limit]}
        return render(request, 'templates/recommendations/recommendation_list.html', context)
    else:
        # 默认返回JSON
        return JsonResponse({
            'success': True,
            'type': rec_type,
            'count': len(products_data),
            'recommendations': products_data
        })

@login_required
def user_recommendations(request):
    """
    用户推荐页面
    显示给用户的个性化推荐
    """
    recommender = SimpleRecommender(request.user)
    recommendations = recommender.recommend_for_user(12)
    
    # 获取其他类型的推荐用于展示
    hot_products = recommender.recommend_hot_products(6)
    new_products = recommender.recommend_new_products(6)
    featured_products = recommender.recommend_featured_products(6)
    
    context = {
        'personalized_recommendations': recommendations,
        'hot_products': hot_products,
        'new_products': new_products,
        'featured_products': featured_products,
    }
    
    return render(request, 'recommendations/user_recommendations.html', context)