# products/views.py
"""
商品应用视图模块
处理商品相关的HTTP请求和响应，包括商品展示、搜索、筛选等功能
"""

# 导入Django核心模块
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.db.models import Q, Count, Avg, Min, Max
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone
import json

# 导入当前应用模型
from .models import Product, Category, Inventory, Color, Size, ProductImage, ProductAttributeValue
# 导入购物车模型
from cart.models import Cart, CartItem


class ProductListView(ListView):
    """
    商品列表视图类
    继承自ListView，用于展示商品列表页面
    支持商品搜索、筛选、排序和分页功能
    """
    model = Product
    template_name = 'products/product_list.html'  # 模板文件路径
    context_object_name = 'products'  # 模板中使用的变量名
    paginate_by = 12  # 每页显示12个商品
    
    def get_queryset(self):
        """
        重写父类方法，获取商品查询集
        支持按分类、搜索关键词、价格范围进行筛选
        支持多种排序方式
        """
        # 基础查询：只获取已上架的商品，并使用select_related优化关联查询
        queryset = Product.objects.filter(status='published').select_related('category')
        
        # ---------------------------
        # 分类筛选（使用分类ID而不是slug）
        # ---------------------------
        category_id = self.request.GET.get('category')
        if category_id and category_id.isdigit():
            # 根据分类ID获取分类对象，不存在则返回404
            category = get_object_or_404(Category, id=int(category_id))
            # 筛选属于该分类的商品
            queryset = queryset.filter(category=category)
        
        # ---------------------------
        # 搜索功能
        # ---------------------------
        search_query = self.request.GET.get('q')
        if search_query:
            # 使用Q对象进行复杂查询，支持在多个字段中搜索
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # 商品名称包含搜索词
                Q(description__icontains=search_query) |  # 商品描述包含搜索词
                Q(short_description__icontains=search_query) |  # 商品短描述包含搜索词
                Q(category__name__icontains=search_query)  # 分类名称包含搜索词
            )
        
        # ---------------------------
        # 价格范围筛选
        # ---------------------------
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price and min_price.replace('.', '', 1).isdigit():
            # 筛选价格大于等于最低价的商品
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price and max_price.replace('.', '', 1).isdigit():
            # 筛选价格小于等于最高价的商品
            queryset = queryset.filter(price__lte=float(max_price))
        
        # ---------------------------
        # 排序功能
        # ---------------------------
        sort_by = self.request.GET.get('sort', 'created_at')
        if sort_by == 'price_asc':
            # 价格升序
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            # 价格降序
            queryset = queryset.order_by('-price')
        elif sort_by == 'sales':
            # 销量降序
            queryset = queryset.order_by('-sales_count')
        elif sort_by == 'new':
            # 最新上架
            queryset = queryset.order_by('-created_at')
        else:
            # 默认按创建时间降序
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        添加上下文数据
        将筛选条件、分类列表等信息传递给模板
        """
        # 获取父类的上下文数据
        context = super().get_context_data(**kwargs)
        
        # ---------------------------
        # 添加分类列表
        # ---------------------------
        # 获取所有激活状态的分类
        context['categories'] = Category.objects.filter(is_active=True)
        
        # ---------------------------
        # 添加筛选参数到上下文
        # ---------------------------
        context['selected_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort', 'created_at')
        
        # ---------------------------
        # 获取价格范围统计数据
        # ---------------------------
        # 计算所有商品的最低和最高价格，用于价格筛选器
        price_range = Product.objects.filter(status='published').aggregate(
            min_price=Min('price'),  # 最低价格
            max_price=Max('price')   # 最高价格
        )
        context['price_range'] = price_range
        
        return context


class ProductDetailView(DetailView):
    """
    商品详情视图类
    继承自DetailView，用于展示单个商品的详细信息
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'  # 模板中使用的商品变量名
    
    def get_object(self, queryset=None):
        """
        获取商品对象，并增加商品浏览量
        每次访问商品详情页，浏览量加1
        """
        # 调用父类方法获取商品对象
        obj = super().get_object(queryset)
        # 增加商品浏览量
        obj.view_count += 1
        # 只更新view_count字段，避免覆盖其他字段
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        """
        添加上下文数据
        包括商品图片、属性、库存、相关商品等信息
        """
        # 获取父类的上下文数据
        context = super().get_context_data(**kwargs)
        product = self.object  # 当前商品对象
        
        # ---------------------------
        # 商品图片
        # ---------------------------
        # 获取商品的所有图片，主图优先显示
        context['images'] = product.images.all().order_by('-is_main', 'order')
        
        # ---------------------------
        # 商品属性
        # ---------------------------
        # 获取商品的所有属性值，并预取关联的属性对象
        context['attributes'] = product.attributes.select_related('attribute')
        
        # ---------------------------
        # 库存信息 - 修复：直接使用Inventory模型查询
        # ---------------------------
        # 获取有库存的SKU
        inventory_items = Inventory.objects.filter(
            product=product,
            is_active=True, 
            count__gt=0
        )
        
        # 获取可用的颜色
        context['available_colors'] = Color.objects.filter(
            id__in=inventory_items.values_list('color_id', flat=True).distinct()
        )
        
        # 获取可用的尺寸
        context['available_sizes'] = Size.objects.filter(
            id__in=inventory_items.values_list('size_id', flat=True).distinct()
        )
        
        # ---------------------------
        # 相关商品
        # ---------------------------
        # 获取同一分类下的其他商品，随机取4个
        context['related_products'] = Product.objects.filter(
            status='published',
            category=product.category
        ).exclude(id=product.id).order_by('?')[:4]  # 使用order_by('?')随机排序
        
        # ---------------------------
        # 添加到购物车时需要的产品ID
        # ---------------------------
        context['product_id'] = product.id
        
        return context


@login_required
def add_to_cart_from_detail(request, product_id):
    """
    从商品详情页添加到购物车视图函数
    处理商品详情页的"加入购物车"表单提交
    
    参数:
        request: HTTP请求对象
        product_id: 商品ID
    
    返回:
        重定向到购物车页面或商品详情页
    """
    # 只处理POST请求
    if request.method == 'POST':
        # 获取商品对象，确保商品已上架
        product = get_object_or_404(Product, id=product_id, status='published')
        
        # ---------------------------
        # 获取表单数据
        # ---------------------------
        quantity = int(request.POST.get('quantity', 1))  # 商品数量，默认为1
        color_id = request.POST.get('color')  # 颜色ID（可选）
        size_id = request.POST.get('size')    # 尺寸ID（可选）
        
        # ---------------------------
        # 验证数据
        # ---------------------------
        if quantity < 1:
            messages.error(request, '数量必须大于0')
            return redirect('products:product_detail', pk=product_id)
        
        # ---------------------------
        # 验证库存 - 修复：直接查询Inventory模型
        # ---------------------------
        # 基础库存查询：有库存且激活的SKU
        inventory_query = Inventory.objects.filter(
            product=product,
            count__gte=quantity,
            is_active=True
        )
        
        # 如果有颜色选择，添加颜色筛选
        if color_id:
            inventory_query = inventory_query.filter(color_id=color_id)
        
        # 如果有尺寸选择，添加尺寸筛选
        if size_id:
            inventory_query = inventory_query.filter(size_id=size_id)
        
        # 检查是否存在符合条件的库存
        if not inventory_query.exists():
            messages.error(request, '所选规格库存不足')
            return redirect('products:product_detail', pk=product_id)
        
        # ---------------------------
        # 获取或创建购物车
        # ---------------------------
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # ---------------------------
        # 处理商品添加到购物车 - 修复：当前CartItem关联的是Product模型
        # 注意：这里的设计可能需要根据你的业务需求调整
        # 如果CartItem应该关联Inventory而不是Product，需要修改模型关系
        # ---------------------------
        # 获取第一个符合条件的库存（如果有规格选择）
        if color_id or size_id:
            inventory = inventory_query.first()
            # TODO: 如果你的CartItem需要关联到具体的Inventory，需要修改这里
            # 当前设计是CartItem关联Product，所以这里仍然使用product
        
        # 创建或更新购物车项
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,  # 注意：这里关联的是Product，不是Inventory
            defaults={'quantity': quantity}
        )
        
        if not created:
            # 如果购物车项已存在，增加数量
            cart_item.quantity += quantity
            cart_item.save()
        
        # ---------------------------
        # 操作成功，返回提示信息
        # ---------------------------
        messages.success(request, f'已成功添加 {product.name} 到购物车')
        return redirect('cart:cart_detail')
    
    # 如果不是POST请求，重定向到商品列表
    return redirect('products:product_list')


class CategoryListView(ListView):
    """
    分类列表视图类
    展示所有顶级商品分类
    """
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        获取顶级分类（没有父分类的分类）
        """
        return Category.objects.filter(parent=None, is_active=True)
    
    def get_context_data(self, **kwargs):
        """
        添加上下文数据
        为每个分类计算商品数量
        """
        context = super().get_context_data(**kwargs)
        
        # 为每个分类添加商品数量统计
        for category in context['categories']:
            # 统计该分类及其所有子分类下的商品数量
            # 注意：Category模型目前没有get_descendants方法，需要添加或修改
            # 暂时只统计直接属于该分类的商品
            category.product_count = Product.objects.filter(
                category=category,  # 修改：只统计直接分类
                status='published'
            ).count()
        
        return context


def get_inventory_data(request, product_id):
    """
    获取商品库存数据接口（AJAX）
    用于前端动态加载商品的库存信息（颜色、尺寸、价格）
    
    参数:
        request: HTTP请求对象
        product_id: 商品ID
    
    返回:
        JSON响应，包含库存数据
    """
    # 只处理AJAX GET请求
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 获取商品对象
        product = get_object_or_404(Product, id=product_id)
        
        # 初始化库存数据结构
        inventory_data = {}
        
        # 获取有库存的SKU - 修复：直接查询Inventory模型
        inventory_items = Inventory.objects.filter(
            product=product,
            is_active=True, 
            count__gt=0
        )
        
        # ---------------------------
        # 按颜色分组组织数据
        # ---------------------------
        for color in Color.objects.filter(inventory__in=inventory_items).distinct():
            # 颜色数据对象
            color_data = {
                'name': color.name,  # 颜色名称
                'code': color.code,  # 颜色代码（十六进制）
                'image': color.image.url if color.image else '',  # 颜色图片URL
                'sizes': []  # 该颜色下的尺寸列表
            }
            
            # 获取该颜色下的所有尺寸
            sizes = Size.objects.filter(
                inventory__in=inventory_items.filter(color=color)
            ).distinct()
            
            # 为每个尺寸添加库存信息
            for size in sizes:
                # 获取该颜色尺寸组合的具体库存
                inventory = inventory_items.filter(color=color, size=size).first()
                if inventory:
                    color_data['sizes'].append({
                        'id': size.id,  # 尺寸ID
                        'name': size.name,  # 尺寸名称
                        'stock': inventory.count,  # 库存数量
                        'price': float(inventory.get_price())  # 价格
                    })
            
            # 只添加有尺寸数据的颜色
            if color_data['sizes']:
                inventory_data[color.id] = color_data
        
        # 返回JSON响应
        return JsonResponse({
            'success': True,
            'inventory': inventory_data
        })
    
    # 如果不是AJAX GET请求，返回错误
    return JsonResponse({'success': False, 'error': '无效请求'}, status=400)


@require_POST
@login_required
def quick_add_to_cart(request, product_id):
    """
    快速添加到购物车视图（AJAX接口）
    用于商品列表页的快速购买功能
    
    参数:
        request: HTTP请求对象
        product_id: 商品ID
    
    返回:
        JSON响应，包含操作结果和购物车信息
    """
    # 只处理AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 解析JSON请求体
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))  # 获取数量，默认为1
        
        # ---------------------------
        # 验证数量
        # ---------------------------
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': '数量必须大于0'
            })
        
        # 获取商品对象
        product = get_object_or_404(Product, id=product_id, status='published')
        
        # ---------------------------
        # 验证库存 - 使用Product的总库存
        # ---------------------------
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'error': f'库存不足，当前库存: {product.stock}'
            })
        
        # ---------------------------
        # 获取或创建购物车
        # ---------------------------
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # ---------------------------
        # 添加商品到购物车
        # ---------------------------
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # 如果购物车项已存在，增加数量
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # ---------------------------
        # 计算购物车最新信息
        # ---------------------------
        cart_info = {
            'item_count': cart.get_item_count(),  # 购物车商品总数
            'total_price': float(cart.get_total_price()),  # 购物车总金额
            'item_name': product.name,  # 刚添加的商品名称
            'quantity': cart_item.quantity  # 当前购物车项数量
        }
        
        # 返回成功响应
        return JsonResponse({
            'success': True,
            'message': f'已添加 {product.name} 到购物车',
            'cart': cart_info
        })
    
    # 如果不是AJAX请求，返回错误
    return JsonResponse({'success': False, 'error': '无效请求'}, status=400)


class FeaturedProductsView(ListView):
    """
    推荐商品视图类
    展示所有标记为推荐的商品
    """
    template_name = 'products/featured_products.html'
    context_object_name = 'products'
    paginate_by = 8  # 每页显示8个商品
    
    def get_queryset(self):
        """
        获取推荐商品查询集
        筛选条件：已上架、标记为推荐
        """
        queryset = Product.objects.filter(
            status='published',  # 已上架
            is_featured=True     # 推荐商品
        ).select_related('category').order_by('-created_at')  # 按创建时间降序
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        添加上下文数据
        设置页面标题
        """
        context = super().get_context_data(**kwargs)
        context['title'] = '推荐商品'
        return context


class NewArrivalsView(ListView):
    """
    新品上架视图类
    展示最近30天内上架的商品
    """
    template_name = 'products/new_arrivals.html'
    context_object_name = 'products'
    paginate_by = 8
    
    def get_queryset(self):
        """
        获取新品查询集
        筛选条件：已上架、创建时间在30天内
        """
        # 计算30天前的时间
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        
        queryset = Product.objects.filter(
            status='published',
            created_at__gte=thirty_days_ago  # 创建时间大于等于30天前
        ).select_related('category').order_by('-created_at')
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        添加上下文数据
        设置页面标题
        """
        context = super().get_context_data(**kwargs)
        context['title'] = '新品上架'
        return context


class SaleProductsView(ListView):
    """
    特价商品视图类
    展示有原价和现价差异的商品（打折商品）
    注意：需要为Product模型添加oldprice字段
    """
    template_name = 'products/sale_products.html'
    context_object_name = 'products'
    paginate_by = 8
    
    def get_queryset(self):
        """
        获取特价商品查询集
        筛选条件：有原价、已上架
        为每个商品计算折扣率
        """
        queryset = Product.objects.filter(
            status='published',
            # 注意：需要为Product模型添加oldprice字段
            # oldprice__gt=0  # 有原价（表示是特价商品）
        ).select_related('category').order_by('-created_at')
        
        # 为每个商品计算折扣率（如果模型有oldprice字段）
        for product in queryset:
            # 临时处理：使用price的80%作为原价示例
            # 实际应用中需要为Product模型添加oldprice字段
            if hasattr(product, 'oldprice') and product.oldprice and product.oldprice > 0:
                product.discount_rate = int((1 - (product.price / product.oldprice)) * 100)
            else:
                # 如果没有oldprice字段，设置为0折扣
                product.discount_rate = 0
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        添加上下文数据
        设置页面标题
        """
        context = super().get_context_data(**kwargs)
        context['title'] = '特价商品'
        return context


def search_suggestions(request):
    """
    搜索建议接口（AJAX）
    根据用户输入提供搜索建议
    
    参数:
        request: HTTP请求对象
    
    返回:
        JSON响应，包含搜索建议列表
    """
    # 只处理AJAX GET请求
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 获取搜索关键词，去除首尾空格
        query = request.GET.get('q', '').strip()
        
        # 如果关键词长度小于2，返回空建议
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # ---------------------------
        # 搜索商品名称
        # ---------------------------
        products = Product.objects.filter(
            name__icontains=query,  # 名称包含搜索词
            status='published'      # 已上架商品
        ).values('id', 'name')[:10]  # 最多返回10个
        
        # ---------------------------
        # 搜索分类名称
        # ---------------------------
        categories = Category.objects.filter(
            name__icontains=query,  # 分类名称包含搜索词
            is_active=True          # 激活的分类
        ).values('id', 'name')[:5]  # 最多返回5个
        
        # 初始化建议列表
        suggestions = []
        
        # ---------------------------
        # 添加商品建议
        # ---------------------------
        for product in products:
            suggestions.append({
                'type': 'product',  # 建议类型：商品
                'id': product['id'],  # 商品ID
                'name': product['name'],  # 商品名称
                'url': f"/products/{product['id']}/"  # 商品详情页URL
            })
        
        # ---------------------------
        # 添加分类建议
        # ---------------------------
        for category in categories:
            suggestions.append({
                'type': 'category',  # 建议类型：分类
                'id': category['id'],  # 分类ID
                'name': category['name'],  # 分类名称
                'url': f"/products/?category={category['id']}"  # 分类商品列表URL
            })
        
        return JsonResponse({'suggestions': suggestions})
    
    # 默认返回空建议
    return JsonResponse({'suggestions': []})


def home(request):
    """
    首页视图函数
    展示网站的首页，包含多种商品推荐
    
    参数:
        request: HTTP请求对象
    
    返回:
        渲染首页模板
    """
    # ---------------------------
    # 推荐商品
    # ---------------------------
    featured_products = Product.objects.filter(
        status='published',  # 已上架
        is_featured=True     # 推荐商品
    ).order_by('-created_at')[:8]  # 按创建时间降序，取8个
    
    # ---------------------------
    # 新品商品
    # ---------------------------
    new_products = Product.objects.filter(
        status='published'
    ).order_by('-created_at')[:8]  # 最新创建的商品
    
    # ---------------------------
    # 热销商品
    # ---------------------------
    hot_products = Product.objects.filter(
        status='published'
    ).order_by('-sales_count')[:8]  # 按销量降序，取8个
    
    # ---------------------------
    # 顶级分类
    # ---------------------------
    categories = Category.objects.filter(
        is_active=True,  # 激活的分类
        parent=None      # 顶级分类（没有父分类）
    )[:6]  # 取6个分类
    
    # ---------------------------
    # 准备上下文数据
    # ---------------------------
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'hot_products': hot_products,
        'categories': categories,
    }
    
    # 渲染首页模板
    return render(request, 'products/home.html', context)