import pytest
import json
from app.models.user import User
from app.utils.auth import generate_token

def test_admin_create_user(client, init_database):
    """测试管理员创建用户"""
    # 创建管理员并登录
    admin = User(username='admin', employee_id='ADMIN1', role='SUPER_ADMIN')
    admin.set_password('admin123')
    init_database.session.add(admin)
    init_database.session.commit()
    
    # 获取管理员令牌
    token = generate_token(admin.id, admin.role)
    
    # 使用令牌创建新用户
    new_user_data = {
        'username': 'newuser',
        'password': 'pass123',
        'employee_id': 'EMP200',
        'full_name': 'New User',
        'gender': 'Female',
        'age': 30
    }
    
    response = client.post('/api/users/', 
                          data=json.dumps(new_user_data),
                          content_type='application/json',
                          headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['username'] == 'newuser'
    assert data['employee_id'] == 'EMP200'
    
    # 验证用户已创建
    assert User.query.filter_by(username='newuser').first() is not None

def test_admin_list_users(client, init_database):
    """测试管理员列出所有用户"""
    # 创建管理员和普通用户
    admin = User(username='admin', employee_id='ADMIN1', role='SUPER_ADMIN')
    admin.set_password('admin123')
    
    user1 = User(username='user1', employee_id='EMP101')
    user1.set_password('pass123')
    
    user2 = User(username='user2', employee_id='EMP102')
    user2.set_password('pass123')
    
    init_database.session.add_all([admin, user1, user2])
    init_database.session.commit()
    
    # 获取管理员令牌
    token = generate_token(admin.id, admin.role)
    
    # 请求用户列表
    response = client.get('/api/users/', 
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 3  # 至少有三个用户

def test_normal_user_cannot_access_admin_routes(client, init_database):
    """测试普通用户无法访问管理员路由"""
    # 创建普通用户
    user = User(username='normaluser', employee_id='EMP301', role='NORMAL_ADMIN')
    user.set_password('pass123')
    init_database.session.add(user)
    init_database.session.commit()
    
    # 获取普通用户令牌
    token = generate_token(user.id, user.role)
    
    # 尝试访问仅管理员可用的路由
    response = client.get('/api/users/', 
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应 - 应该返回403禁止访问
    assert response.status_code == 403

def test_update_own_profile(client, init_database):
    """测试用户更新自己的资料"""
    # 创建用户
    user = User(username='profileuser', employee_id='EMP401', full_name='Old Name')
    user.set_password('pass123')
    init_database.session.add(user)
    init_database.session.commit()
    
    # 获取用户令牌
    token = generate_token(user.id, user.role)
    
    # 更新资料
    update_data = {
        'full_name': 'New Full Name',
        'gender': 'Male',
        'age': 35
    }
    
    response = client.put('/api/users/me', 
                         data=json.dumps(update_data),
                         content_type='application/json',
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['full_name'] == 'New Full Name'
    assert data['gender'] == 'Male'
    assert data['age'] == 35
    
    # 验证数据库已更新
    updated_user = User.query.filter_by(id=user.id).first()
    assert updated_user.full_name == 'New Full Name'

