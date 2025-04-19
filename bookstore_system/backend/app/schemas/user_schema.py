from marshmallow import fields, validate, validates, ValidationError
from .. import ma
from ..models.user import User

class UserSchema(ma.SQLAlchemySchema):
    """用户信息序列化Schema，用于API响应"""
    class Meta:
        model = User
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    username = ma.auto_field()
    full_name = ma.auto_field()
    employee_id = ma.auto_field()
    gender = ma.auto_field()
    age = ma.auto_field()
    role = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # hashed_password 不会被序列化到响应中

class UserRegistrationSchema(ma.Schema):
    """用户注册Schema，用于创建新用户"""
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    password = fields.String(required=True, validate=validate.Length(min=6), load_only=True)
    full_name = fields.String(validate=validate.Length(max=100))
    employee_id = fields.String(required=True, validate=validate.Length(max=50))
    gender = fields.String(validate=validate.Length(max=10))
    age = fields.Integer(validate=validate.Range(min=18, max=100))
    role = fields.String(validate=validate.OneOf(['NORMAL_ADMIN', 'SUPER_ADMIN']), default='NORMAL_ADMIN')
    
    @validates('username')
    def validate_username(self, username):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=username).first():
            raise ValidationError('用户名已存在')
            
    @validates('employee_id')
    def validate_employee_id(self, employee_id):
        """验证员工ID是否已存在"""
        if User.query.filter_by(employee_id=employee_id).first():
            raise ValidationError('员工ID已存在')

class LoginSchema(ma.Schema):
    """登录Schema，用于用户登录验证"""
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

