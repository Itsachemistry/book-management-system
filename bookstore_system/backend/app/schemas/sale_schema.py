from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, validates_schema
from ..models.sale import Sale, SaleItem, SALE_STATUS
from ..models.book import Book
from ..database import db
from decimal import Decimal
from datetime import datetime, timezone
from ..models.transaction import Transaction
from ..models.transaction import TRANSACTION_TYPES
import uuid


class SaleItemSchema(Schema):
    """销售订单项 Schema"""
    id = fields.Integer(dump_only=True)
    sale_id = fields.Integer(dump_only=True)
    book_id = fields.Integer(required=True)
    
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    sale_price = fields.Decimal(required=True, validate=validate.Range(min=0))
    subtotal = fields.Decimal(dump_only=True)
    
    # 书籍信息 (只在响应中)
    book = fields.Nested('BookSchema', dump_only=True)
    
    @validates('book_id')
    def validate_book_exists(self, value, **kwargs):
        book = db.session.get(Book, value)
        if not book:
            raise ValidationError(f"书籍ID {value} 不存在")
        
        if not book.is_active:
            raise ValidationError(f"书籍 '{book.name}' 已下架")
        
        return value


class SaleSchema(Schema):
    """销售订单 Schema"""
    id = fields.Integer(dump_only=True)
    sale_number = fields.String(dump_only=True)
    sale_date = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    total_amount = fields.Decimal(dump_only=True)
    customer_name = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)
    
    user_id = fields.Integer(dump_only=True)
    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'username', 'full_name'))
    
    items = fields.List(fields.Nested(SaleItemSchema), required=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class SaleCreateSchema(Schema):
    """用于创建销售订单的 Schema"""
    customer_name = fields.String(allow_none=True)
    contact = fields.String(allow_none=True)
    payment_method = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)
    
    items = fields.List(
        fields.Nested(SaleItemSchema), 
        required=True,
        validate=validate.Length(min=1, error='订单必须包含至少一个商品')
    )
    
    @validates_schema
    def validate_items(self, data, **kwargs):
        errors = {}
        for idx, item in enumerate(data.get('items', [])):
            book = db.session.get(Book, item['book_id'])
            if not book:
                errors.setdefault('items', {})[idx] = {
                    'book_id': [f"书籍ID {item['book_id']} 不存在"]
                }
            elif not book.is_active:
                errors.setdefault('items', {})[idx] = {
                    'book_id': [f"书籍 '{book.name}' 已下架"]
                }
        
        if errors:
            raise ValidationError(errors)


class SaleUpdateSchema(Schema):
    """用于更新销售订单的 Schema"""
    customer_name = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)


class SaleQuerySchema(Schema):
    """用于验证查询销售列表的查询参数"""
    status = fields.String(validate=validate.OneOf(SALE_STATUS.keys()), allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=10, validate=validate.Range(min=1, max=100))