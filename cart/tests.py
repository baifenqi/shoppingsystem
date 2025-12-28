# tests.py
# 单元测试文件，包含购物车模块的测试用例
# 导入Django测试框架
from django.test import TestCase, Client
# 导入Django用户模型
from django.contrib.auth import get_user_model  # 修改这行
# 导入Django的URL反转函数
from django.urls import reverse
# 导入当前应用的模型
from .models import Cart, CartItem
# 导入产品模型（假设products应用已注册）
from products.models import Product
# 获取用户模型
User = get_user_model()  # 添加这行

class CartModelTests(TestCase):
    """购物车模型测试类，测试模型的各种方法"""
    def setUp(self):
        """测试前的初始化方法，每个测试方法执行前都会调用"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',  # 用户名
            password='testpass123'  # 密码
        )
        # 创建测试商品
        self.product = Product.objects.create(
            name='测试商品',  # 商品名称
            price=100.00,  # 商品价格
            stock=10  # 商品库存
        )
    
    def test_cart_creation(self):
        """测试购物车创建功能"""
        # 创建一个购物车
        cart = Cart.objects.create(user=self.user)
        # 断言购物车用户名称正确
        self.assertEqual(cart.user.username, 'testuser')
        # 断言购物车的字符串表示正确
        self.assertEqual(str(cart), 'testuser的购物车')
    
    def test_cart_item_total_price(self):
        """测试购物车项总价计算方法"""
        # 创建一个购物车
        cart = Cart.objects.create(user=self.user)
        # 创建一个购物车项，数量为3
        cart_item = CartItem.objects.create(
            cart=cart,  # 关联购物车
            product=self.product,  # 关联商品
            quantity=3  # 数量为3
        )
        # 断言购物车项总价计算正确（100 * 3 = 300）
        self.assertEqual(cart_item.total_price(), 300.00)
    
    def test_cart_total_price(self):
        """测试购物车总价计算方法"""
        # 创建一个购物车
        cart = Cart.objects.create(user=self.user)
        # 添加第一个购物车项，数量为2
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        # 创建第二个测试商品
        product2 = Product.objects.create(
            name='测试商品2',
            price=50.00,
            stock=5
        )
        # 添加第二个购物车项，数量为1
        CartItem.objects.create(
            cart=cart,
            product=product2,
            quantity=1
        )
        # 断言购物车总价计算正确（100 * 2 + 50 * 1 = 250）
        self.assertEqual(cart.total_price(), 250.00)
    
    def test_cart_item_count(self):
        """测试购物车商品数量统计方法"""
        # 创建一个购物车
        cart = Cart.objects.create(user=self.user)
        # 添加一个购物车项
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )
        # 断言购物车商品数量为1
        self.assertEqual(cart.item_count(), 1)

class CartViewTests(TestCase):
    """购物车视图测试类，测试视图函数的功能"""
    def setUp(self):
        """测试前的初始化方法，每个测试方法执行前都会调用"""
        # 创建测试客户端，用于模拟HTTP请求
        self.client = Client()
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # 创建测试商品
        self.product = Product.objects.create(
            name='测试商品',
            price=100.00,
            stock=10
        )
        # 创建测试购物车
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_detail_requires_login(self):
        """测试购物车详情页面需要登录访问"""
        # 未登录状态下访问购物车详情页
        response = self.client.get(reverse('cart:cart_detail'))
        # 断言返回302重定向状态码（跳转到登录页）
        self.assertEqual(response.status_code, 302)
    
    def test_cart_detail_view(self):
        """测试购物车详情页面正常显示"""
        # 登录测试用户
        self.client.login(username='testuser', password='testpass123')
        # 访问购物车详情页
        response = self.client.get(reverse('cart:cart_detail'))
        # 断言返回200成功状态码
        self.assertEqual(response.status_code, 200)
        # 断言使用正确的模板文件
        self.assertTemplateUsed(response, 'cart/cart_detail.html')
    
    def test_add_to_cart_view(self):
        """测试添加商品到购物车功能"""
        # 登录测试用户
        self.client.login(username='testuser', password='testpass123')
        # 发送POST请求添加商品到购物车，数量为2
        response = self.client.post(
            reverse('cart:add_to_cart', args=[self.product.id]),  # URL反转
            {'quantity': 2}  # POST数据
        )
        # 断言返回302重定向状态码（成功添加后重定向）
        self.assertEqual(response.status_code, 302)
        # 断言购物车项数量为1
        self.assertEqual(CartItem.objects.count(), 1)
    
    def test_remove_from_cart_view(self):
        """测试从购物车移除商品功能"""
        # 创建一个测试购物车项
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        # 登录测试用户
        self.client.login(username='testuser', password='testpass123')
        # 发送GET请求移除购物车项
        response = self.client.get(
            reverse('cart:remove_from_cart', args=[cart_item.id])
        )
        # 断言返回302重定向状态码（成功移除后重定向）
        self.assertEqual(response.status_code, 302)
        # 断言购物车项数量为0
        self.assertEqual(CartItem.objects.count(), 0)