import pytest
import json
from app.models.user import User

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

def test_get_me_with_token(client, init_database):
    """测试带有有效令牌获取当前用户"""
    # 创建测试用户并登录
    user = User(username='testuser', employee_id='EMP100')
    user.set_password('password123')
    init_database.session.add(user)
    init_database.session.commit()
    
    # 登录获取令牌
    login_response = client.post('/api/auth/login', 
                              data=json.dumps({'username': 'testuser', 'password': 'password123'}),
                              content_type='application/json')
    login_data = json.loads(login_response.data)
    token = login_data['token']
    
    # 使用令牌请求/me端点
    response = client.get('/api/auth/me', 
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['username'] == 'testuser'

def test_get_me_without_token(client):
    """测试不带令牌获取当前用户"""
    # 未提供令牌请求/me端点
    response = client.get('/api/auth/me')
    
    # 验证响应
    assert response.status_code == 401

