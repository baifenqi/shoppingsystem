"""
推荐系统URL配置
"""
from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # 推荐API接口
    path('api/recommend/', views.get_recommendations, name='get_recommendations'),
    
    # 用户推荐页面
    path('recommendations/', views.user_recommendations, name='user_recommendations'),
]