"""
推荐算法实现
提供商品推荐的算法逻辑
"""
from django.db.models import Count, Q
from products.models import Product, Category
from cart.models import Cart, CartItem
from django.contrib.auth.models import User
import random
from collections import defaultdict

class SimpleRecommender:
    """
    简化推荐算法类
    提供多种推荐策略
    """
    
    def __init__(self, user=None):
        """
        初始化推荐器
        :param user: 当前用户对象，如果为None则提供通用推荐
        """
        self.user = user
    
    def recommend_for_user(self, limit=6):
        """
        为用户推荐商品
        根据用户情况选择最适合的推荐策略
        
        :param limit: 返回推荐商品数量
        :return: 推荐商品列表
        """
        if not self.user or not self.user.is_authenticated:
            # 未登录用户：返回热门商品
            return self.recommend_hot_products(limit)
        
        # 检查用户购物车
        try:
            cart = Cart.objects.get(user=self.user)
            cart_items = cart.items.count()
            
            if cart_items > 0:
                # 有购物车商品：基于购物车内容推荐
                return self.recommend_based_on_cart(limit)
            else:
                # 无购物车商品：基于用户历史行为推荐
                return self.recommend_based_on_history(limit)
        except Cart.DoesNotExist:
            # 用户无购物车：返回热门商品
            return self.recommend_hot_products(limit)
    
    def recommend_based_on_cart(self, limit=6):
        """
        基于购物车内容推荐商品
        策略：找到购物车中商品同分类的其他商品，或互补商品
        
        :param limit: 返回推荐商品数量
        :return: 推荐商品列表
        """
        try:
            cart = Cart.objects.get(user=self.user)
            cart_items = cart.items.select_related('product', 'product__category').all()
            
            if not cart_items:
                return self.recommend_hot_products(limit)
            
            # 1. 收集购物车中商品分类
            categories = []
            for item in cart_items:
                if item.product.category:
                    categories.append(item.product.category)
            
            # 2. 查找同分类的热门商品
            if categories:
                # 去重分类
                category_ids = list(set([c.id for c in categories if c]))
                
                # 查找同分类商品，排除已在购物车中的商品
                cart_product_ids = [item.product.id for item in cart_items]
                
                similar_products = Product.objects.filter(
                    category_id__in=category_ids,
                    status='published'
                ).exclude(
                    id__in=cart_product_ids
                ).order_by('-sales_count', '-view_count')[:limit*2]
                if category_ids:
                    try:
                        similar_products = Product.objects.filter(
                             category_id__in=category_ids,
                              status='published'
                        ).exclude(
                             id__in=cart_product_ids
                        ).order_by('-sales_count', '-view_count')[:limit*2]
                    except:
                         similar_products = Product.objects.none()
                else:
                    similar_products = Product.objects.none()

                
                # 如果同分类商品不足，补充其他推荐
                if len(similar_products) >= limit:
                    return list(similar_products[:limit])
                
                # 补充其他策略的商品
                return self._combine_recommendations(similar_products, limit)
        
        except Cart.DoesNotExist:
            pass
        
        # 如果上述策略失败，返回热门商品
        return self.recommend_hot_products(limit)
    
    def recommend_based_on_history(self, limit=6):
        """
        基于用户历史行为推荐商品
        简化版：查找用户最近浏览的分类中的热门商品
        
        :param limit: 返回推荐商品数量
        :return: 推荐商品列表
        """
        # 简化策略：返回热门商品
        # 实际项目中可以从用户浏览记录、购买记录等提取偏好
        return self.recommend_hot_products(limit)
    
    def recommend_hot_products(self, limit=6):
        """
        推荐热门商品
        基于销量和浏览量的综合排序
        
        :param limit: 返回推荐商品数量
        :return: 热门商品列表
        """
        # 计算热门度分数 = 销量 + 浏览量/10
        # 简化实现：按销量和浏览量排序
        hot_products = Product.objects.filter(
            status='published'
        ).order_by('-sales_count', '-view_count')[:limit]
        
        return list(hot_products)
    
    def recommend_new_products(self, limit=6):
        """
        推荐新品
        最近上架的商品
        
        :param limit: 返回推荐商品数量
        :return: 新品列表
        """
        new_products = Product.objects.filter(
            status='published'
        ).order_by('-created_at')[:limit]
        
        return list(new_products)
    
    def recommend_featured_products(self, limit=6):
        """
        推荐精选商品
        管理员标记为推荐的商品
        
        :param limit: 返回推荐商品数量
        :return: 精选商品列表
        """
        featured_products = Product.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-created_at')[:limit]
        
        return list(featured_products)
    
    def recommend_related_products(self, product, limit=6):
        """
        推荐相关商品
        基于指定商品推荐相似商品
        
        :param product: 基础商品对象
        :param limit: 返回推荐商品数量
        :return: 相关商品列表
        """
        if not product.category:
            return self.recommend_hot_products(limit)
        
        # 查找同分类商品
        related_products = Product.objects.filter(
            category=product.category,
            status='published'
        ).exclude(
            id=product.id
        ).order_by('-sales_count', '-view_count')[:limit]
        
        return list(related_products)
    
    def _combine_recommendations(self, products, limit):
        """
        组合多种推荐策略的结果
        确保返回指定数量的商品
        
        :param products: 已找到的商品列表
        :param limit: 需要返回的商品数量
        :return: 组合后的商品列表
        """
        result = list(products)
        
        # 如果商品数量不足，补充热门商品
        if len(result) < limit:
            needed = limit - len(result)
            hot_products = self.recommend_hot_products(needed)
            
            # 过滤掉已存在的商品
            existing_ids = [p.id for p in result]
            for product in hot_products:
                if product.id not in existing_ids:
                    result.append(product)
        
        return result[:limit]