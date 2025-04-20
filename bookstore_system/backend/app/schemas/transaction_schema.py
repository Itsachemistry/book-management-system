from marshmallow import Schema, fields, validate
from ..models.transaction import TRANSACTION_TYPES


class TransactionSchema(Schema):
    """财务交易记录 Schema"""
    id = fields.Integer(dump_only=True)
    transaction_type = fields.String(dump_only=True)
    amount = fields.Decimal(dump_only=True)
    description = fields.String(dump_only=True)
    transaction_date = fields.DateTime(dump_only=True)
    
    user_id = fields.Integer(dump_only=True)
    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'username', 'full_name'))
    
    reference_id = fields.Integer(dump_only=True)
    reference_type = fields.String(dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TransactionQuerySchema(Schema):
    """用于验证查询财务记录的查询参数"""
    transaction_type = fields.String(validate=validate.OneOf(TRANSACTION_TYPES.keys()))
    start_date = fields.Date()
    end_date = fields.Date()
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=10, validate=validate.Range(min=1, max=100))