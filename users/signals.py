# users/signals.py
# 用户信号处理器
# 定义用户相关的信号处理逻辑
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CustomUser

# 获取用户模型
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建后自动创建相关资料
    在新用户注册成功后执行"""
    if created:
        # 可以在此创建关联的用户资料
        print(f"用户 {instance.username} 已创建")
        
        # 示例：发送欢迎邮件（在实际项目中实现）
        # send_welcome_email(instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时执行的操作"""
    # 可以在此添加用户保存时的逻辑
    pass

# 可添加更多信号处理器，如：
# - 用户登录信号
# - 用户密码修改信号
# - 用户登出信号