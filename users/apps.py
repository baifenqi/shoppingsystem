# users/apps.py
# 用户应用配置类
# 定义users应用的配置信息
from django.apps import AppConfig

class UsersConfig(AppConfig):
    """用户应用配置类
    继承自Django的AppConfig，用于配置users应用"""
    default_auto_field = 'django.db.models.BigAutoField'  # 默认主键字段类型
    name = 'users'  # 应用名称，与目录名称一致
    verbose_name = '用户管理'  # 在Django管理后台显示的名称
    
    def ready(self):
        """应用就绪时调用的方法
        在此方法中注册信号处理器等初始化操作"""
        import users.signals  # 导入信号模块
