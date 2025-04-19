import pytest
import json
import uuid
from ..app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, ORDER_STATUS
from ..app.models.transaction import Transaction, TRANSACTION_TYPES
from ..app.models.book import Book
from ..app.utils.auth import generate_token


def create_test_order(client, admin_token, order_data=None):
    """辅助函数：创建测试订单"""
    if order_data is None:
        # 创建默认测试数据
        order_data = {
            'supplier': '默认测试供应商',
            'remarks': '测试备注',
            'items': [
                {
                    'title': '测试图书',
                    'author': '测试作者',
                    'publisher': '测试出版社',
                    'isbn': f'978{uuid.uuid4().hex[:10]}',
                    'quantity': 5,
                    'purchase_price': 25.00,
                    'suggested_retail_price': 49.90
                }
            ]
        }
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    return client.post('/api/procurement/orders', json=order_data, headers=headers)


def test_create_order(client, admin_token, book_fixture):
    """测试创建订单"""
    # 使用固定的书籍ID
    order_data = {
        'supplier': '测试供应商',
        'remarks': '测试备注',
        'items': [
            {
                'book_id': book_fixture.id,
                'quantity': 5,
                'purchase_price': 25.00
            },
            {
                'title': '新书测试',
                'author': '测试作者',
                'publisher': '测试出版社',
                'isbn': '9787000000000',
                'quantity': 10,
                'purchase_price': 30.00,
                'suggested_retail_price': 49.90
            }
        ]
    }
    
    response = create_test_order(client, admin_token, order_data)
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert 'id' in data
    assert 'order_number' in data
    assert data['status'] == ORDER_STATUS['UNPAID']
    assert len(data['items']) == 2
    assert data['total_amount'] == '425.00'  # (5*25) + (10*30)


def test_get_orders(client, admin_token):
    """测试获取订单列表"""
    # 先创建几个订单
    create_test_order(client, admin_token)
    create_test_order(client, admin_token)
    
    # 获取订单列表
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/procurement/orders', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'orders' in data
    assert 'pagination' in data
    assert len(data['orders']) >= 2
    assert data['pagination']['total'] >= 2


def test_get_order_detail(client, admin_token):
    """测试获取单个订单详情"""
    # 创建订单
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    # 获取订单详情
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get(f'/api/procurement/orders/{order_id}', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['id'] == order_id
    assert 'items' in data
    assert len(data['items']) > 0


def test_update_order(client, admin_token):
    """测试更新订单基本信息"""
    # 创建订单
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    # 更新订单
    update_data = {
        'supplier': '更新后的供应商',
        'remarks': '更新后的备注'
    }
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.put(f'/api/procurement/orders/{order_id}', json=update_data, headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['supplier'] == update_data['supplier']
    assert data['remarks'] == update_data['remarks']


def test_pay_order(client, admin_token):
    """测试支付订单"""
    # 创建订单
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    # 支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'message' in data
    assert data['order']['status'] == ORDER_STATUS['PAID']
    
    # 验证是否创建了财务记录
    with client.application.app_context():
        transaction = Transaction.query.filter_by(
            reference_id=order_id, 
            reference_type='purchase_order'
        ).first()
        
        assert transaction is not None
        assert transaction.transaction_type == TRANSACTION_TYPES['EXPENSE']
        assert float(transaction.amount) == float(create_data['total_amount'])


def test_return_order(client, admin_token):
    """测试退货订单"""
    # 创建订单
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    # 退货订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post(f'/api/procurement/orders/{order_id}/return', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'message' in data
    assert data['order']['status'] == ORDER_STATUS['RETURNED']


def test_stock_in(client, admin_token, book_fixture):
    """测试图书入库"""
    # 创建订单
    order_data = {
        'supplier': '测试供应商',
        'remarks': '测试备注',
        'items': [
            {
                'book_id': book_fixture.id,
                'quantity': 10,
                'purchase_price': 25.00
            }
        ]
    }
    
    create_response = create_test_order(client, admin_token, order_data)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    # 先支付订单
    headers = {'Authorization': f'Bearer {admin_token}'}
    client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    
    # 初始库存
    initial_quantity = book_fixture.quantity
    
    # 入库
    response = client.post(f'/api/procurement/orders/{order_id}/stock-in', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'message' in data
    assert data['order']['status'] == ORDER_STATUS['STOCKED']
    
    # 验证库存更新
    with client.application.app_context():
        updated_book = Book.query.get(book_fixture.id)
        assert updated_book.quantity == initial_quantity + 10


def test_pay_already_paid_order(client, admin_token):
    """测试支付已支付的订单"""
    # 创建订单并支付
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    
    # 尝试再次支付
    response = client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'description' in data


def test_stock_in_unpaid_order(client, admin_token):
    """测试对未支付订单进行入库"""
    # 创建订单但不支付
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    # 尝试入库
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post(f'/api/procurement/orders/{order_id}/stock-in', headers=headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'description' in data


def test_return_paid_order(client, admin_token):
    """测试退货已支付订单"""
    # 创建订单并支付
    create_response = create_test_order(client, admin_token)
    create_data = json.loads(create_response.data)
    order_id = create_data['id']
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    client.post(f'/api/procurement/orders/{order_id}/pay', headers=headers)
    
    # 尝试退货
    response = client.post(f'/api/procurement/orders/{order_id}/return', headers=headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'description' in data