"""
推荐应用配置
"""
from django.apps import AppConfig

class RecommendationsConfig(AppConfig):
    """推荐应用配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    verbose_name = '推荐系统'