import pytest
import json
from app.models.user import User
# 导入 generate_token
from app.utils.auth import generate_token

def test_login_success(client, init_database):
    """测试成功登录"""
    # 创建测试用户
    user = User(username='testuser', employee_id='EMP100')
    user.set_password('password123')
    init_database.session.add(user)
    init_database.session.commit()
    
    # 发送登录请求
    response = client.post('/api/auth/login', 
                          data=json.dumps({'username': 'testuser', 'password': 'password123'}),
                          content_type='application/json')
    
    # 验证响应
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'token' in data
    assert data['user']['username'] == 'testuser'

def test_login_invalid_credentials(client, init_database):
    """测试无效凭据登录"""
    # 创建测试用户
    user = User(username='testuser', employee_id='EMP100')
    user.set_password('password123')
    init_database.session.add(user)
    init_database.session.commit()
    
    # 发送错误密码的登录请求
    response = client.post('/api/auth/login', 
                          data=json.dumps({'username': 'testuser', 'password': 'wrongpass'}),
                          content_type='application/json')
    
    # 验证响应
    assert response.status_code == 401

def test_get_me_with_token(client, init_database, app): # 添加 app fixture
    """测试带有有效令牌获取当前用户"""
    # 创建测试用户并登录
    user = User(username='testuser', employee_id='EMP100')
    user.set_password('password123')
    init_database.session.add(user)
    init_database.session.commit()

    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(user.id, user.role)

    # 使用令牌请求/me端点
    response = client.get('/api/auth/me',
                         headers={'Authorization': f'Bearer {token}'})

    # 验证响应
    # 检查状态码是否为 200
    assert response.status_code == 200
    # 尝试解析 JSON
    try:
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
    except json.JSONDecodeError:
        pytest.fail(f"Failed to decode JSON. Response data: {response.data.decode()}")

def test_get_me_without_token(client):
    """测试不带令牌获取当前用户"""
    # 未提供令牌请求/me端点
    response = client.get('/api/auth/me')
    
    # 验证响应
    assert response.status_code == 401

