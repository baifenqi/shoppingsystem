# users/models.py
# 用户数据模型定义
# 定义用户相关的数据库模型和业务逻辑
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """自定义用户模型
    继承自Django的AbstractUser，可添加自定义字段"""
    # 添加自定义字段
    phone_number = models.CharField(
        '手机号码',  # 字段标签
        max_length=15,  # 最大长度
        blank=True,  # 允许为空
        null=True,  # 允许数据库NULL值
        unique=True  # 唯一约束
    )
    
    address = models.TextField(
        '地址',  # 字段标签
        max_length=200,  # 最大长度
        blank=True,  # 允许为空
        null=True  # 允许数据库NULL值
    )
    
    date_of_birth = models.DateField(
        '出生日期',  # 字段标签
        blank=True,  # 允许为空
        null=True  # 允许数据库NULL值
    )
    
    profile_picture = models.ImageField(
        '头像',  # 字段标签
        upload_to='profile_pics/',  # 上传路径
        blank=True,  # 允许为空
        null=True  # 允许数据库NULL值
    )
    
    class Meta:
        """模型元数据配置"""
        verbose_name = '用户'  # 单数名称
        verbose_name_plural = '用户'  # 复数名称
        ordering = ['-date_joined']  # 默认按注册时间降序
    
    def __str__(self):
        """返回用户对象的字符串表示"""
        return self.username
    
    def get_full_name(self):
        """获取用户全名"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """获取用户简称"""
        return self.first_name