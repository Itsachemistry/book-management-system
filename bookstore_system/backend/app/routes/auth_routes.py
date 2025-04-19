from flask import Blueprint, request, jsonify, g
from ..models.user import User
from ..schemas.user_schema import UserSchema, LoginSchema
from ..utils.auth import generate_token
from ..utils.decorators import login_required
from .. import db

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录API
    
    请求体:
    {
        "username": "用户名",
        "password": "密码"
    }
    
    返回:
    {
        "token": "JWT令牌",
        "user": {用户信息对象}
    }
    """
    # 反序列化并验证请求数据
    schema = LoginSchema()
    data = schema.load(request.get_json())
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证密码
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码不正确'}), 401
    
    # 生成令牌
    token = generate_token(user.id, user.role)
    
    # 序列化用户信息
    user_schema = UserSchema()
    user_data = user_schema.dump(user)
    
    return jsonify({
        'token': token,
        'user': user_data
    })

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    获取当前登录用户信息API
    
    需要Authorization: Bearer <token>请求头
    
    返回:
    {用户信息对象}
    """
    # 用户信息已在login_required装饰器中附加到g.user
    user_schema = UserSchema()
    return jsonify(user_schema.dump(g.user))

