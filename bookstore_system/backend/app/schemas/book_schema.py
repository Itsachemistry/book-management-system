from marshmallow import fields, validates, ValidationError, validate, EXCLUDE
from .. import ma
from ..models.book import Book
import decimal # 导入 decimal 模块

class BookSchema(ma.SQLAlchemySchema):
    """用于序列化和反序列化Book模型的Schema"""
    class Meta:
        model = Book
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    isbn = ma.auto_field()
    name = ma.auto_field()
    publisher = ma.auto_field()
    author = ma.auto_field()
    retail_price = ma.auto_field()
    quantity = ma.auto_field()
    is_active = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)

class BookCreateSchema(ma.Schema):
    """用于创建新书籍的Schema"""
    isbn = fields.String(required=True)
    name = fields.String(required=True)
    publisher = fields.String(required=False, allow_none=True)
    author = fields.String(required=False, allow_none=True)
    # 使用 Decimal 字段以匹配模型的 Numeric 类型，提高精度
    retail_price = fields.Decimal(required=True, places=2, as_string=False) 
    quantity = fields.Integer(load_default=0)

    @validates('isbn')
    def validate_isbn(self, value, **kwargs): # 添加 **kwargs
        """验证ISBN是否已存在"""
        if Book.query.filter_by(isbn=value).first():
            raise ValidationError('此ISBN已存在')

    @validates('retail_price')
    def validate_retail_price(self, value, **kwargs): # 添加 **kwargs
        """验证零售价格是否为正数"""
        # value 现在是 Decimal 类型
        if value <= decimal.Decimal(0):
            raise ValidationError('零售价格必须为正数')

    @validates('quantity')
    def validate_quantity(self, value, **kwargs): # 添加 **kwargs
        """验证库存数量是否为非负数"""
        if value < 0:
            raise ValidationError('库存数量不能为负数')

class BookUpdateSchema(ma.Schema):
    """用于更新书籍的Schema"""
    # 添加Meta类配置，设置unknown=EXCLUDE来忽略未知字段
    class Meta:
        unknown = EXCLUDE  # 自动排除未知字段而不是引发错误
        
    # 进一步简化字段定义，让验证更宽松
    isbn = fields.String(allow_none=True)  
    name = fields.String(allow_none=True)
    author = fields.String(allow_none=True)
    publisher = fields.String(allow_none=True)
    retail_price = fields.Raw() # 接受任何类型的价格数据
    quantity = fields.Raw() # 接受任何类型的数量数据
    is_active = fields.Boolean(allow_none=True)

class BookQuerySchema(ma.Schema):
    """用于验证查询书籍列表的查询参数"""
    search = fields.String(required=False, allow_none=True)
    page = fields.Integer(load_default=1, validate=fields.validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=fields.validate.Range(min=1, max=100))
    active_only = fields.Boolean(load_default=True)

