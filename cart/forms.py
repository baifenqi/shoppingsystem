# forms.py
# 购物车应用的表单定义文件，定义用于用户输入验证和数据处理的表单类
from django import forms
from .models import CartItem
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product

class AddToCartForm(forms.Form):
    """添加到购物车表单，用于在商品详情页添加商品到购物车"""
    # 商品数量字段
    quantity = forms.IntegerField(
        label='数量',  # 表单标签显示文本
        min_value=1,  # 最小值验证，数量必须大于等于1
        max_value=100,  # 最大值验证，单次添加数量不超过100
        initial=1,  # 表单初始值设为1
        error_messages={
            'required': '请输入商品数量',  # 必填字段错误消息
            'min_value': '数量必须大于0',  # 最小值验证错误消息
            'max_value': '单次最多添加100件'  # 最大值验证错误消息
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Bootstrap样式类
            'min': '1',  # HTML5 min属性
            'max': '100',  # HTML5 max属性
            'style': 'width: 120px;'  # 内联样式设置宽度
        })
    )
    # 商品ID隐藏字段，用于传递商品信息
    product_id = forms.IntegerField(
        widget=forms.HiddenInput()  # 隐藏输入框，不在页面显示
    )

class UpdateCartItemForm(forms.ModelForm):
    """更新购物车项表单，继承自ModelForm用于直接操作模型实例"""
    class Meta:
        """表单元数据配置"""
        model = CartItem  # 关联的模型是CartItem
        fields = ['quantity']  # 只包含数量字段
        labels = {
            'quantity': '数量'  # 字段标签
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',  # Bootstrap小尺寸输入框样式
                'min': '1',  # HTML5最小值属性
                'max': '100',  # HTML5最大值属性
                'style': 'width: 80px; display: inline-block;'  # 内联样式设置
            })
        }
    
    def clean_quantity(self):
        """自定义数量字段验证方法"""
        quantity = self.cleaned_data.get('quantity')  # 获取清理后的数据
        if quantity is None:  # 检查数量是否为None
            raise forms.ValidationError('数量不能为空')
        if quantity < 1:  # 检查数量是否小于1
            raise forms.ValidationError('数量必须大于0')
        if quantity > 100:  # 检查数量是否超过100
            raise forms.ValidationError('单件商品数量不能超过100')
        # 检查库存是否充足
        if hasattr(self.instance, 'product') and self.instance.product:
            if quantity > self.instance.product.stock:
                raise forms.ValidationError(f'库存不足，当前库存: {self.instance.product.stock}')
        return quantity  # 返回验证通过的数量

class CheckoutForm(forms.Form):
    """结算表单，用于收集用户结算时的配送和支付信息"""
    # 收货人姓名字段
    recipient_name = forms.CharField(
        label='收货人姓名',  # 字段标签
        max_length=50,  # 最大长度50字符
        required=True,  # 必填字段
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Bootstrap样式
            'placeholder': '请输入收货人姓名'  # 输入提示
        })
    )
    # 收货人电话字段
    phone_number = forms.CharField(
        label='联系电话',  # 字段标签
        max_length=20,  # 最大长度20字符
        required=True,  # 必填字段
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Bootstrap样式
            'placeholder': '请输入联系电话'  # 输入提示
        })
    )
    # 收货地址字段
    shipping_address = forms.CharField(
        label='收货地址',  # 字段标签
        max_length=200,  # 最大长度200字符
        required=True,  # 必填字段
        widget=forms.Textarea(attrs={
            'class': 'form-control',  # Bootstrap样式
            'rows': 3,  # 显示3行
            'placeholder': '请输入详细的收货地址'  # 输入提示
        })
    )
    # 支付方式选择字段
    payment_method = forms.ChoiceField(
        label='支付方式',  # 字段标签
        choices=[  # 选项列表
            ('alipay', '支付宝'),  # 支付宝选项
            ('wechat', '微信支付'),  # 微信支付选项
            ('bank', '银行卡支付'),  # 银行卡支付选项
        ],
        initial='alipay',  # 默认选择支付宝
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'  # Bootstrap单选按钮样式
        })
    )
    # 订单备注字段
    order_notes = forms.CharField(
        label='订单备注',  # 字段标签
        required=False,  # 非必填字段
        widget=forms.Textarea(attrs={
            'class': 'form-control',  # Bootstrap样式
            'rows': 2,  # 显示2行
            'placeholder': '请输入订单备注（选填）'  # 输入提示
        })
    )