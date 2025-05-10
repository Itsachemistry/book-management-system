from marshmallow import Schema, fields, validate, ValidationError, post_load
from datetime import datetime
from ..models.transaction import TRANSACTION_TYPES

class TransactionSchema(Schema):
    """交易记录序列化模式"""
    id = fields.Integer(dump_only=True)
    amount = fields.Decimal(required=True, as_string=True)
    type = fields.String(required=True, validate=validate.OneOf(TRANSACTION_TYPES.values()))
    description = fields.String()
    reference_id = fields.String()
    reference_type = fields.String()
    transaction_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    
    # 为了前端兼容性，使用transaction_type作为type的别名
    transaction_type = fields.Method('get_transaction_type', dump_only=True)
    
    def get_transaction_type(self, obj):
        return obj.type

class TransactionQuerySchema(Schema):
    """交易记录查询参数序列化模式"""
    transaction_type = fields.String(validate=validate.OneOf([*TRANSACTION_TYPES.values(), '']))
    start_date = fields.String(validate=validate.Length(min=1))  # 允许字符串格式的日期
    end_date = fields.String(validate=validate.Length(min=1))    # 允许字符串格式的日期
    page = fields.Integer(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), load_default=20)
    
    @post_load
    def process_dates(self, data, **kwargs):
        """处理日期字段，如果是字符串则转换为日期对象"""
        if 'start_date' in data and data['start_date']:
            if isinstance(data['start_date'], str):
                try:
                    data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d')
                except ValueError:
                    raise ValidationError('开始日期格式无效，应为YYYY-MM-DD', field_name='start_date')
        
        if 'end_date' in data and data['end_date']:
            if isinstance(data['end_date'], str):
                try:
                    data['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d')
                except ValueError:
                    raise ValidationError('结束日期格式无效，应为YYYY-MM-DD', field_name='end_date')
        
        return data