# apps.py
# Django应用配置文件，定义购物车应用的配置信息
# 导入Django应用配置基类
from django.apps import AppConfig

class CartConfig(AppConfig):
    """购物车应用的配置类，继承自AppConfig"""
    # 设置默认的自动生成主键字段类型，使用64位BigAutoField
    default_auto_field = 'django.db.models.BigAutoField'
    # 指定应用在Python路径中的名称，与文件夹名称一致
    name = 'cart'
    # 设置在Django管理后台显示的应用名称（中文）
    verbose_name = '购物车管理'
    
    def ready(self):
        """应用就绪时自动调用的方法，用于执行初始化操作"""
        # 导入应用的信号处理器，在应用启动时注册信号
        import cart.signals