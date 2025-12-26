# cart/templatetags/cart_tags.py
# 导入Django模板库，用于注册自定义过滤器
from django import template

# 创建模板库实例（固定写法，必须有这一行）
register = template.Library()

# 注册自定义过滤器：@register.filter 是装饰器，标记这是一个模板过滤器
@register.filter(name='mul')  # name='mul' 指定过滤器名称为mul，模板中用{{ 值|mul:参数 }}调用
def mul(value, arg):
    """
    自定义乘法过滤器：用于计算购物车商品小计（数量 * 单价）
    :param value: 第一个值（模板中|左边的内容,如item.quantity)
    :param arg: 第二个值（模板中|右边的内容,如item.product.price)
    :return: 两个值的乘积,若转换失败返回0(避免页面报错)
    """
    try:
        # 先转换为浮点数（兼容整数/小数价格），再计算乘积
        return float(value) * float(arg)
    except (ValueError, TypeError):
        # 异常处理：若输入非数字（如空值、字符串），返回0，避免页面崩溃
        return 0