from functools import wraps
from flask import request, abort, g
from .auth import verify_token
from ..models.user import User
from ..database import db # 导入 db
import sys # Add sys for stderr printing

def login_required(f):
    """
    用于保护需要登录才能访问的API路由的装饰器
    验证Authorization请求头中的Bearer令牌
    将当前用户附加到g.user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Debug print: 进入装饰器
        print("\nEntering login_required decorator", file=sys.stderr) 
        # 获取Authorization请求头
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            # Debug print: 失败原因
            print("login_required: Aborting 401 - Missing Authorization header", file=sys.stderr) 
            abort(401, description="缺少Authorization请求头")
        
        # 确保格式正确：Bearer <token>
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            # Debug print: 失败原因
            print("login_required: Aborting 401 - Invalid Authorization header format", file=sys.stderr) 
            abort(401, description="Authorization请求头格式无效")
        
        token = parts[1]
        # 验证令牌
        payload = verify_token(token)
        
        if not payload:
            # Debug print: 失败原因
            print("login_required: Aborting 401 - verify_token returned None", file=sys.stderr) 
            abort(401, description="无效或过期的令牌")
        
        # Debug print: 验证后的负载
        print(f"login_required: Token payload verified: {payload}", file=sys.stderr) 
        
        # 获取用户并附加到g上下文
        user_id_str = payload.get('sub') # 获取字符串形式的 user_id
        if user_id_str is None:
             # Debug print: 失败原因
            print("login_required: Aborting 401 - 'sub' claim missing in token payload", file=sys.stderr)
            abort(401, description="令牌负载无效")
            
        try:
            user_id = int(user_id_str) # 将字符串转换回整数
        except ValueError:
             # Debug print: 失败原因
            print(f"login_required: Aborting 401 - Invalid 'sub' claim format: {user_id_str}", file=sys.stderr)
            abort(401, description="令牌负载无效")

        # Debug print: 正在查找的用户ID
        print(f"login_required: Looking for user with ID: {user_id}", file=sys.stderr) 
        # 使用 db.session.get 替代 User.query.get
        user = db.session.get(User, user_id) # 使用整数 ID 查询
        if not user:
             # Debug print: 失败原因
            print(f"login_required: Aborting 401 - User with ID {user_id} not found in DB", file=sys.stderr) 
            abort(401, description="用户不存在")
            
        # Debug print: 找到的用户
        print(f"login_required: User found: {user}. Attaching to g.user", file=sys.stderr) 
        g.user = user
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    用于保护需要管理员权限才能访问的API路由的装饰器
    在login_required基础上增加角色检查 (允许 ADMIN 和 SUPER_ADMIN)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
         # Debug print: 进入装饰器
        print("\nEntering admin_required decorator", file=sys.stderr)
        # 先验证用户已登录
        login_decorated = login_required(lambda: None) 
        login_decorated() # This call will abort if login fails
        
        # If login_decorated() didn't abort, g.user should be set.
        # Debug print: 登录检查通过，检查角色
        print(f"admin_required: Login check passed. Checking role for user: {g.user}", file=sys.stderr) 
        
        # 检查用户是否为 ADMIN 或 SUPER_ADMIN
        allowed_roles = ['ADMIN', 'SUPER_ADMIN']
        if g.user.role not in allowed_roles:
            # Debug print: 角色检查失败
            print(f"admin_required: Aborting 403 - User role '{g.user.role}' not in {allowed_roles}", file=sys.stderr) 
            abort(403, description="需要管理员权限")
            
        # Debug print: 角色检查通过
        print("admin_required: Role check passed.", file=sys.stderr) 
        return f(*args, **kwargs)
    
    return decorated_function

