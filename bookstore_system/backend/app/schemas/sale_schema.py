from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_dump
from ..models.sale import SALE_STATUS
from ..models.book import Book
from ..database import db
from decimal import Decimal
from datetime import datetime, timezone
from ..models.transaction import Transaction
from ..models.transaction import TRANSACTION_TYPES
import uuid


class SaleItemSchema(Schema):
    """销售订单项的序列化Schema"""
    id = fields.Int(dump_only=True)  # 添加ID字段用于唯一标识
    book_id = fields.Integer(required=True)  # 确保是整数
    quantity = fields.Integer(required=True, validate=lambda x: x > 0)  # 确保是正整数
    price = fields.Decimal(places=2, required=True)  # 确保是小数
    
    # 添加关联的书籍信息
    book = fields.Nested('BookSchema', only=('id', 'isbn', 'name'), dump_only=True)


class SaleCreateSchema(Schema):
    """创建销售订单的输入Schema"""
    customer_name = fields.Str(allow_none=True)
    contact = fields.Str(allow_none=True)
    payment_method = fields.Str(load_default='CASH')
    remarks = fields.Str(allow_none=True)
    items = fields.List(
        fields.Nested(SaleItemSchema), 
        required=True, 
        validate=lambda x: len(x) > 0
    )


class SaleUpdateSchema(Schema):
    """更新销售订单状态的Schema"""
    status = fields.Str(required=True, validate=lambda x: x in SALE_STATUS.values())


class SaleSchema(Schema):
    """完整的销售订单输出Schema"""
    id = fields.Int(dump_only=True)
    sale_number = fields.Str()
    sale_date = fields.DateTime()
    status = fields.Str()
    total_amount = fields.Decimal(places=2)
    customer_name = fields.Str()
    contact = fields.Str()
    payment_method = fields.Str()
    remarks = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # 关联的用户信息
    user = fields.Nested('UserSchema', only=('id', 'username', 'full_name'), dump_only=True)
    
    # 销售项目
    items = fields.List(fields.Nested(SaleItemSchema), dump_only=True)