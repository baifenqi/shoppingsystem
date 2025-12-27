# users/admin.py
# 用户管理后台配置
# 配置User模型在Django管理后台的显示和编辑方式
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# 导入自定义User模型
from .models import CustomUser

# 注册自定义用户模型到管理后台
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """自定义用户模型管理后台配置
    继承自Django默认的UserAdmin，可自定义显示字段"""
    # 列表页显示字段
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    # 列表页筛选器
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'date_joined']
    # 搜索字段
    search_fields = ['username', 'email', 'first_name', 'last_name']
    # 字段分组布局
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    # 添加用户时的字段布局
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    ordering = ['username']  # 默认排序