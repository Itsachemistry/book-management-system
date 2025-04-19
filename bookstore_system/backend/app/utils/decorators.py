from functools import wraps
from flask import request, abort, g
from .auth import verify_token
from ..models.user import User

def login_required(f):
    """
    用于保护需要登录才能访问的API路由的装饰器
    验证Authorization请求头中的Bearer令牌
    将当前用户附加到g.user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Authorization请求头
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, description="缺少Authorization请求头")
        
        # 确保格式正确：Bearer <token>
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            abort(401, description="Authorization请求头格式无效")
        
        token = parts[1]
        # 验证令牌
        payload = verify_token(token)
        
        if not payload:
            abort(401, description="无效或过期的令牌")
        
        # 获取用户并附加到g上下文
        user = User.query.get(payload['sub'])
        if not user:
            abort(401, description="用户不存在")
            
        g.user = user
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    用于保护需要管理员权限才能访问的API路由的装饰器
    在login_required基础上增加角色检查
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 先验证用户已登录
        login_decorated = login_required(lambda: None)
        login_decorated()
        
        # 检查用户是否为超级管理员
        if g.user.role != 'SUPER_ADMIN':
            abort(403, description="需要管理员权限")
            
        return f(*args, **kwargs)
    
    return decorated_function

