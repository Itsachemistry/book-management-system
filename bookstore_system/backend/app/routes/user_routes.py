from flask import Blueprint, request, jsonify, g
from ..models.user import User
from ..schemas.user_schema import UserSchema, UserRegistrationSchema
from ..utils.decorators import admin_required, login_required
from .. import db
from marshmallow import ValidationError  # 添加导入

# 创建蓝图
user_bp = Blueprint('users', __name__)

@user_bp.route('/', methods=['POST'])
@admin_required
def create_user():
    """
    创建新用户API（仅管理员）
    
    请求体:
    {
        "username": "用户名",
        "password": "密码",
        "full_name": "全名",
        "employee_id": "员工ID",
        "gender": "性别",
        "age": 年龄,
        "role": "角色"
    }
    
    返回:
    {新创建的用户信息}
    """
    try:
        # 反序列化并验证请求数据
        schema = UserRegistrationSchema()
        data = schema.load(request.get_json())
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            full_name=data.get('full_name'),
            employee_id=data['employee_id'],
            gender=data.get('gender'),
            age=data.get('age'),
            role=data.get('role', 'NORMAL_ADMIN')
        )
        
        # 设置密码
        new_user.set_password(data['password'])
        
        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()
        
        # 返回创建的用户
        user_schema = UserSchema()
        return jsonify(user_schema.dump(new_user)), 201
    
    except ValidationError as err:
        # 捕获验证错误，返回400状态码和详细错误信息
        return jsonify({"error": "验证错误", "details": err.messages}), 400
    except Exception as e:
        # 捕获其他异常，回滚事务
        db.session.rollback()
        # 可以记录详细日志
        print(f"创建用户时发生错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500

@user_bp.route('/', methods=['GET'])
@admin_required
def get_users():
    """
    获取所有用户列表API（仅管理员）
    
    返回:
    [用户列表]
    """
    users = User.query.all()
    schema = UserSchema(many=True)
    return jsonify(schema.dump(users))

@user_bp.route('/me', methods=['PUT'])
@login_required
def update_profile():
    """
    更新当前用户个人资料API
    
    请求体:
    {
        "full_name": "新全名",
        "gender": "新性别",
        "age": 新年龄
    }
    
    返回:
    {更新后的用户信息}
    """
    # 获取当前用户
    user = g.user
    
    # 获取请求数据
    data = request.get_json()
    
    # 允许更新的字段
    allowed_fields = ['full_name', 'gender', 'age']
    
    # 更新字段
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # 保存更改
    db.session.commit()
    
    # 返回更新后的用户信息
    schema = UserSchema()
    return jsonify(schema.dump(user))

@user_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_id):
    """
    获取单个用户信息API（仅管理员）
    
    返回:
    {用户信息}
    """
    user = User.query.get_or_404(user_id)
    schema = UserSchema()
    return jsonify(schema.dump(user))

@user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    更新用户信息API（仅管理员）
    
    请求体:
    {
        "full_name": "全名",
        "employee_id": "员工ID",
        "gender": "性别",
        "age": 年龄,
        "role": "角色"
    }
    
    返回:
    {更新后的用户信息}
    """
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # 允许更新的字段
        allowed_fields = ['full_name', 'employee_id', 'gender', 'age', 'role']
        
        # 更新字段
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 可选更新密码
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # 保存更改
        db.session.commit()
        
        # 返回更新后的用户信息
        schema = UserSchema()
        return jsonify(schema.dump(user))
        
    except Exception as e:
        db.session.rollback()
        print(f"更新用户时发生错误: {str(e)}")
        return jsonify({"error": "更新用户失败"}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    删除用户API（仅管理员）
    
    返回:
    {"message": "用户已删除"}
    """
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "用户已删除"})
    except Exception as e:
        db.session.rollback()
        print(f"删除用户时发生错误: {str(e)}")
        return jsonify({"error": "删除用户失败"}), 500

