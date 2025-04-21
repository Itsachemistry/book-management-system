import pytest
import json
from app.models.purchase_order import PurchaseOrder, ORDER_STATUS
from app.models.transaction import Transaction, TRANSACTION_TYPES
from app.models.book import Book
from app.utils.auth import generate_token
from app.models.user import User
from app import db

def create_test_order(client, admin_token, order_data=None):
    """辅助函数：创建测试订单"""
    if order_data is None:
        # 创建默认测试数据
        order_data = {
            'supplier': '边界测试供应商',
            'remarks': '边界测试备注',
            'items': [
                {
                    'title': '边界测试图书',
                    'author': '边界测试作者',
                    'publisher': '边界测试出版社',
                    'isbn': '9787000001234',
                    'quantity': 5,
                    'purchase_price': 25.00,
                    'suggested_retail_price': 49.90
                }
            ]
        }
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    return client.post('/api/procurement/orders', json=order_data, headers=headers)

def test_pay_already_paid_order(client, admin_token):
    """测试对已支付订单再次支付的情况"""
    # 创建订单
    response = create_test_order(client, admin_token)
    assert response.status_code == 201
    
    order_data = json.loads(response.data)
    order_id = order_data['id']
    
    # 第一次支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    pay_response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    assert pay_response.status_code == 200
    
    # 尝试再次支付同一个订单
    second_pay_response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    assert second_pay_response.status_code == 400
    
    # 验证错误消息
    error_data = json.loads(second_pay_response.data)
    assert "error" in error_data
    assert "已支付" in error_data["error"]

def test_return_paid_order(client, admin_token):
    """测试尝试退货已支付的订单"""
    # 创建订单
    response = create_test_order(client, admin_token)
    assert response.status_code == 201
    
    order_data = json.loads(response.data)
    order_id = order_data['id']
    
    # 支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    pay_response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    assert pay_response.status_code == 200
    
    # 尝试退货已支付订单
    return_response = client.post(f'/api/procurement/orders/{order_id}/return', headers=headers)
    assert return_response.status_code == 400
    
    # 验证错误消息
    error_data = json.loads(return_response.data)
    assert "error" in error_data
    assert "仅未支付" in error_data["error"] or "仅限未支付" in error_data["error"]

def test_stock_in_unpaid_order(client, admin_token):
    """测试尝试对未支付订单进行入库操作"""
    # 创建订单
    response = create_test_order(client, admin_token)
    assert response.status_code == 201
    
    order_data = json.loads(response.data)
    order_id = order_data['id']
    
    # 尝试对未支付订单入库
    headers = {'Authorization': f'Bearer {admin_token}'}
    stock_in_response = client.post(f'/api/procurement/orders/{order_id}/stock-in', headers=headers)
    assert stock_in_response.status_code == 400
    
    # 验证错误消息
    error_data = json.loads(stock_in_response.data)
    assert "error" in error_data
    assert "仅已支付" in error_data["error"] or "仅限已支付" in error_data["error"]

def test_stock_in_already_stocked_order(client, admin_token):
    """测试对已入库订单再次入库"""
    # 创建订单
    response = create_test_order(client, admin_token)
    assert response.status_code == 201
    
    order_data = json.loads(response.data)
    order_id = order_data['id']
    
    # 支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    pay_response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    assert pay_response.status_code == 200
    
    # 首次入库
    stock_in_response = client.post(f'/api/procurement/orders/{order_id}/stock-in', headers=headers)
    assert stock_in_response.status_code == 200
    
    # 尝试再次入库
    second_stock_in_response = client.post(f'/api/procurement/orders/{order_id}/stock-in', headers=headers)
    assert second_stock_in_response.status_code == 400
    
    # 验证错误消息
    error_data = json.loads(second_stock_in_response.data)
    assert "error" in error_data
    assert "已入库" in error_data["error"] or "已经入库" in error_data["error"]

def test_return_stocked_order(client, admin_token):
    """测试尝试退货已入库的订单"""
    # 创建订单
    response = create_test_order(client, admin_token)
    assert response.status_code == 201
    
    order_data = json.loads(response.data)
    order_id = order_data['id']
    
    # 支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    pay_response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    assert pay_response.status_code == 200
    
    # 入库
    stock_in_response = client.post(f'/api/procurement/orders/{order_id}/stock-in', headers=headers)
    assert stock_in_response.status_code == 200
    
    # 尝试退货已入库订单
    return_response = client.post(f'/api/procurement/orders/{order_id}/return', headers=headers)
    assert return_response.status_code == 400
    
    # 验证错误消息
    error_data = json.loads(return_response.data)
    assert "error" in error_data
    assert "仅未支付" in error_data["error"] or "仅限未支付" in error_data["error"]

def test_normal_user_create_order(client, init_database, app):
    """测试普通用户尝试创建订单"""
    # 创建普通用户
    normal_user = User(username='normal_test', employee_id='EMP001', role='NORMAL_ADMIN')
    normal_user.set_password('password123')
    init_database.session.add(normal_user)
    init_database.session.commit()
    
    # 生成普通用户令牌
    with app.app_context():
        token = generate_token(normal_user.id, normal_user.role)
    
    # 尝试创建订单
    order_data = {
        'supplier': '普通用户测试',
        'remarks': '普通用户不应该能创建订单',
        'items': [
            {
                'title': '测试图书',
                'author': '测试作者',
                'publisher': '测试出版社',
                'isbn': '9787000005678',
                'quantity': 3,
                'purchase_price': 20.00,
                'suggested_retail_price': 40.00
            }
        ]
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/procurement/orders', json=order_data, headers=headers)
    
    # 验证结果 - 应返回403禁止访问
    assert response.status_code == 403

def test_update_non_unpaid_order(client, admin_token):
    """测试尝试更新非"未支付"状态的订单"""
    # 创建订单
    response = create_test_order(client, admin_token)
    assert response.status_code == 201
    
    order_data = json.loads(response.data)
    order_id = order_data['id']
    
    # 支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    pay_response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    assert pay_response.status_code == 200
    
    # 尝试更新已支付订单
    update_data = {
        'supplier': '更新的供应商',
        'remarks': '这个更新应该被拒绝'
    }
    
    update_response = client.put(f'/api/procurement/orders/{order_id}', json=update_data, headers=headers)
    assert update_response.status_code == 400
    
    # 验证错误消息
    error_data = json.loads(update_response.data)
    assert "error" in error_data
    assert "只能修改未支付" in error_data["error"]

def test_invalid_order_id(client, admin_token):
    """测试使用无效的订单ID"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # 尝试查看不存在的订单详情
    response = client.get('/api/procurement/orders/99999', headers=headers)
    assert response.status_code == 404
    
    # 尝试更新不存在的订单
    update_data = {'supplier': '新供应商'}
    response = client.put('/api/procurement/orders/99999', json=update_data, headers=headers)
    assert response.status_code == 404
    
    # 尝试支付不存在的订单
    response = client.post('/api/procurement/orders/99999/pay', headers=headers)
    assert response.status_code == 404
