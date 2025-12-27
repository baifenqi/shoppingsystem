# users/tests.py
# 用户单元测试
# 包含用户模型和视图的测试用例
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import CustomUser
from .forms import UserRegisterForm

class UserModelTests(TestCase):
    """用户模型测试类"""
    def setUp(self):
        """测试初始化"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_string_representation(self):
        """测试用户字符串表示"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_get_full_name(self):
        """测试获取用户全名"""
        self.user.first_name = '张'
        self.user.last_name = '三'
        self.assertEqual(self.user.get_full_name(), '张 三')
    
    def test_user_with_custom_fields(self):
        """测试用户自定义字段"""
        user = CustomUser.objects.create_user(
            username='customuser',
            password='testpass123',
            phone_number='13800138000',
            address='北京市朝阳区'
        )
        self.assertEqual(user.phone_number, '13800138000')
        self.assertEqual(user.address, '北京市朝阳区')

class UserViewTests(TestCase):
    """用户视图测试类"""
    def setUp(self):
        """测试初始化"""
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_register_view(self):
        """测试注册视图"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_post(self):
        """测试注册POST请求"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        self.assertEqual(response.status_code, 302)  # 注册成功后重定向
    
    def test_login_view(self):
        """测试登录视图"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_post(self):
        """测试登录POST请求"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # 登录成功后重定向
    
    def test_logout_view(self):
        """测试登出视图"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # 登出后重定向
    
    def test_profile_view_requires_login(self):
        """测试个人中心需要登录"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # 未登录时重定向到登录页
    
    def test_profile_view_authenticated(self):
        """测试已登录用户访问个人中心"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')