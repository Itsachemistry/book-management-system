import jwt
from datetime import datetime, timedelta
from flask import current_app
import sys # Add sys for stderr printing

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
        'sub': str(user_id), # 将 user_id 转换为字符串
        'role': role
    }
    
    secret_key = current_app.config.get('SECRET_KEY')
    # Debug print: 显示正在使用的密钥（部分）
    print(f"Generating token with key: {secret_key[:5]}...{secret_key[-5:]}", file=sys.stderr) 
    
    # 使用应用的SECRET_KEY签名
    token = jwt.encode(
        payload,
        secret_key,
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
    secret_key = current_app.config.get('SECRET_KEY')
    # Debug print: 显示正在验证的令牌（部分）和使用的密钥（部分）
    print(f"\nVerifying token: {token[:10]}...", file=sys.stderr) 
    print(f"Using key: {secret_key[:5]}...{secret_key[-5:]}", file=sys.stderr) 
    
    try:
        # 解码并验证令牌
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=['HS256']
        )
        # Debug print: 验证成功及负载内容
        print(f"Token verified successfully. Payload: {payload}", file=sys.stderr) 
        return payload
    except jwt.ExpiredSignatureError:
        # 令牌已过期
        # Debug print: 验证失败原因
        print("Token verification failed: ExpiredSignatureError", file=sys.stderr) 
        return None
    except jwt.InvalidTokenError as e:
        # 令牌无效
        # Debug print: 验证失败原因
        print(f"Token verification failed: InvalidTokenError - {e}", file=sys.stderr) 
        return None
    except Exception as e:
        # 其他潜在错误
        # Debug print: 验证失败原因
        print(f"Token verification failed: Unexpected error - {e}", file=sys.stderr) 
        return None

