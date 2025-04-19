import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_token(user_id, role):
    """
    生成JWT认证令牌
    
    参数:
        user_id: 用户ID
        role: 用户角色
        
    返回:
        token: JWT令牌
    """
    # 设置过期时间（例如24小时）
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'sub': user_id,
        'role': role
    }
    
    # 使用应用的SECRET_KEY签名
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )
    
    return token

def verify_token(token):
    """
    验证JWT令牌
    
    参数:
        token: JWT令牌
        
    返回:
        payload: 解码后的令牌内容，失败则返回None
    """
    try:
        # 解码并验证令牌
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        # 令牌已过期
        return None
    except jwt.InvalidTokenError:
        # 令牌无效
        return None

