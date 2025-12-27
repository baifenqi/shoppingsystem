# users/migrations/0002_alter_customuser_phone_number.py
# 第二个迁移文件 - 修改手机号码字段
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True, verbose_name='手机号码'),
        ),
    ]