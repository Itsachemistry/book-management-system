from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, validates_schema
# 确保正确导入 validates_schema 装饰器
from ..models.purchase_order import PurchaseOrder, PurchaseOrderItem, ORDER_STATUS

class PurchaseOrderItemSchema(Schema):
    """进货订单项 Schema"""
    id = fields.Integer(dump_only=True)
    purchase_order_id = fields.Integer(dump_only=True)
    book_id = fields.Integer(allow_none=True)
    
    # 新书信息，如果 book_id 为空则这些是必填的
    isbn = fields.String(allow_none=True)
    title = fields.String(allow_none=True)
    author = fields.String(allow_none=True)
    publisher = fields.String(allow_none=True)
    
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    purchase_price = fields.Decimal(required=True, validate=validate.Range(min=0))
    suggested_retail_price = fields.Decimal(allow_none=True)
    subtotal = fields.Decimal(dump_only=True)
    
    # 书籍信息 (只在响应中)
    book = fields.Nested('BookSchema', dump_only=True, exclude=('quantity',))
    
    @validates('book_id')
    def validate_book_exists(self, value, **kwargs):  # 添加 **kwargs 参数
        # 如果提供了 book_id 但是在数据库中不存在，验证会失败
        from ..models.book import Book
        if value and not Book.query.get(value):
            raise ValidationError('指定的书籍不存在')
    
    @validates_schema
    def validate_new_book_info(self, data, **kwargs):
        # 如果没有提供 book_id，则 title, author, publisher 是必需的
        if 'book_id' not in data or not data['book_id']:
            for field in ('title', 'author', 'publisher'):
                if field not in data or not data[field]:
                    raise ValidationError(f'对于新书，{field} 是必需的')


class PurchaseOrderSchema(Schema):
    """进货订单 Schema"""
    id = fields.Integer(dump_only=True)
    order_number = fields.String(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    total_amount = fields.Decimal(dump_only=True)
    supplier = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)
    
    user_id = fields.Integer(dump_only=True)
    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'username', 'full_name'))
    
    items = fields.List(fields.Nested(PurchaseOrderItemSchema), required=True, 
                        validate=validate.Length(min=1, error='订单必须包含至少一个商品'))
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PurchaseOrderCreateSchema(Schema):
    """用于创建进货订单的 Schema"""
    # 其他字段定义...
    id = fields.Integer(dump_only=True)
    order_number = fields.String(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    total_amount = fields.Decimal(dump_only=True)
    supplier = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)
    
    user_id = fields.Integer(dump_only=True)
    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'username', 'full_name'))
    
    items = fields.List(fields.Nested(PurchaseOrderItemSchema), required=True, 
                        validate=validate.Length(min=1, error='订单必须包含至少一个商品'))
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates_schema
    def validate_items(self, data, **kwargs):
        # 验证逻辑...
        if not data.get('items') or len(data['items']) == 0:
            raise ValidationError('订单必须包含至少一个项目')
        
        # 其他验证逻辑...


class PurchaseOrderUpdateSchema(Schema):
    """用于更新进货订单的 Schema"""
    supplier = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)


class PurchaseOrderQuerySchema(Schema):
    """用于验证查询进货单列表的查询参数"""
    status = fields.String(validate=validate.OneOf(ORDER_STATUS.keys())) # 验证状态是否有效
    start_date = fields.Date()
    end_date = fields.Date()
    page = fields.Integer(load_default=1, validate=validate.Range(min=1)) # <--- 修改这里
    per_page = fields.Integer(load_default=10, validate=validate.Range(min=1, max=100)) # <--- 修改这里