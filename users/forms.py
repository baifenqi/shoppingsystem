# users/forms.py
# 用户表单定义
# 定义用户相关的表单类
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    """用户注册表单
    继承自Django的UserCreationForm，可添加自定义字段"""
    email = forms.EmailField(
        label='邮箱',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址'
        })
    )
    
    class Meta:
        model = CustomUser  # 关联自定义用户模型
        fields = ['username', 'email', 'password1', 'password2']  # 表单字段
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """初始化表单，为密码字段添加样式"""
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        """验证邮箱是否已存在"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email

class UserLoginForm(AuthenticationForm):
    """用户登录表单
    继承自Django的AuthenticationForm"""
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': '请输入用户名'
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded',
            'placeholder': '请输入密码'
        })
    )
    
    def __init__(self, *args, **kwargs):
        """初始化表单"""
        super().__init__(*args, **kwargs)
        # 可以在此添加额外的初始化逻辑

class ProfileUpdateForm(forms.ModelForm):
    """用户资料更新表单"""
    class Meta:
        model = CustomUser  # 关联自定义用户模型
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'first_name': '名',
            'last_name': '姓',
            'email': '邮箱',
            'phone_number': '手机号码',
            'address': '地址',
            'date_of_birth': '出生日期',
            'profile_picture': '头像',
        }
    
    def clean_phone_number(self):
        """验证手机号码格式"""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError('手机号码必须为数字')
        if phone_number and len(phone_number) != 11:
            raise forms.ValidationError('手机号码必须为11位')
        return phone_number