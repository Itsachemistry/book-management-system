from marshmallow import fields, validates, ValidationError
from .. import ma
from ..models.book import Book

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
    retail_price = fields.Float(required=True)
    quantity = fields.Integer(load_default=0)

    @validates('isbn')
    def validate_isbn(self, value, **kwargs): # 添加 **kwargs
        """验证ISBN是否已存在"""
        if Book.query.filter_by(isbn=value).first():
            raise ValidationError('此ISBN已存在')

    @validates('retail_price')
    def validate_retail_price(self, value, **kwargs): # 添加 **kwargs
        """验证零售价格是否为正数"""
        if value <= 0:
            raise ValidationError('零售价格必须为正数')

    @validates('quantity')
    def validate_quantity(self, value, **kwargs): # 添加 **kwargs
        """验证库存数量是否为非负数"""
        if value < 0:
            raise ValidationError('库存数量不能为负数')

class BookUpdateSchema(ma.Schema):
    """用于更新书籍的Schema"""
    name = fields.String(required=False)
    publisher = fields.String(required=False, allow_none=True)
    author = fields.String(required=False, allow_none=True)
    retail_price = fields.Float(required=False)
    quantity = fields.Integer(required=False)
    is_active = fields.Boolean(required=False)

    @validates('retail_price')
    def validate_retail_price(self, value, **kwargs): # 添加 **kwargs
        """验证零售价格是否为正数"""
        if value is not None and value <= 0:
            raise ValidationError('零售价格必须为正数')

    @validates('quantity')
    def validate_quantity(self, value, **kwargs): # 添加 **kwargs
        """验证库存数量是否为非负数"""
        if value is not None and value < 0:
            raise ValidationError('库存数量不能为负数')

