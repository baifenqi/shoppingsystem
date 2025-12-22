# products/apps.py
# Django应用配置文件，定义商品应用的配置信息
from django.apps import AppConfig

class ProductsConfig(AppConfig):  # 修改类名
    """商品应用的配置类，继承自AppConfig"""
    # 设置默认的自动生成主键字段类型，使用64位BigAutoField
    default_auto_field = 'django.db.models.BigAutoField'
    # 指定应用在Python路径中的名称，与文件夹名称一致
    name = 'products'  # 修改这里
    # 设置在Django管理后台显示的应用名称（中文）
    verbose_name = '商品管理'
    
    def ready(self):
        """应用就绪时自动调用的方法，用于执行初始化操作"""
        # 如果需要信号处理，在这里导入
        import products.signals  # 修改这里