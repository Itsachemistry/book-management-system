import pytest
import json
from app.models.sale import Sale, SaleItem, SALE_STATUS
from app.models.transaction import Transaction, TRANSACTION_TYPES
from app.models.book import Book
from app import db  # 直接导入db对象


def test_create_sale(client, admin_token, book_fixture):
    """测试创建销售记录"""
    initial_book_quantity = 20
    sale_quantity = 2
    expected_quantity_after_sale = initial_book_quantity - sale_quantity

    # 确保书籍有足够库存
    with client.application.app_context():
        # 使用 session.get 获取书籍
        book = db.session.get(Book, book_fixture.id)
        assert book is not None, f"Book with ID {book_fixture.id} not found."
        book.quantity = initial_book_quantity
        db.session.commit()
        # 确认设置成功
        book_check = db.session.get(Book, book_fixture.id)
        assert book_check.quantity == initial_book_quantity

    # 创建销售数据
    sale_data = {
        'customer_name': '测试顾客',
        'contact': '13800138000',
        'payment_method': 'CASH',
        'remarks': '测试销售备注',
        'items': [
            {
                'book_id': book_fixture.id,
                'quantity': sale_quantity,
                'sale_price': float(book_fixture.retail_price)
            }
        ]
    }

    # 发送请求
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post('/api/sales', json=sale_data, headers=headers)

    # 添加诊断输出
    print(f"\n[test_create_sale] 响应状态码: {response.status_code}")
    # print(f"[test_create_sale] 响应内容: {response.data.decode('utf-8')}")

    # 验证响应
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert 'sale_number' in data
    assert data['status'] == SALE_STATUS['COMPLETED']

    # 验证库存是否减少
    with client.application.app_context():
        book_after_sale = db.session.get(Book, book_fixture.id)
        assert book_after_sale.quantity == expected_quantity_after_sale


def test_create_sale_insufficient_stock(client, admin_token, book_fixture):
    """测试库存不足的情况"""
    low_stock_quantity = 3
    requested_quantity = 5

    # 设置较低的库存
    with client.application.app_context():
        # 使用 session.get 获取书籍
        book = db.session.get(Book, book_fixture.id)
        assert book is not None, f"Book with ID {book_fixture.id} not found."
        book.quantity = low_stock_quantity
        db.session.commit()
        # 确认设置成功
        book_check = db.session.get(Book, book_fixture.id)
        print(f"\n[test_create_sale_insufficient_stock] Quantity before request: {book_check.quantity}") # Debug print
        assert book_check.quantity == low_stock_quantity, "Failed to set book quantity in test setup"

    # 创建销售数据
    sale_data = {
        'customer_name': '测试客户',
        'remarks': '测试备注',
        'items': [
            {
                'book_id': book_fixture.id,
                'quantity': requested_quantity,  # 大于库存 (3)
                'sale_price': float(book_fixture.retail_price)
            }
        ]
    }

    # 发送请求
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post('/api/sales', json=sale_data, headers=headers)

    print(f"[test_create_sale_insufficient_stock] Insufficient stock response status: {response.status_code}") # Debug print
    # print(f"[test_create_sale_insufficient_stock] Insufficient stock response data: {response.data.decode('utf-8')}") # Debug print

    # 验证响应 - 应该返回 400
    assert response.status_code == 400, f"Expected status code 400 but got {response.status_code}"
    data = json.loads(response.data)
    assert 'error' in data
    # 更具体的错误检查（如果后端返回结构化错误）
    # Example: assert 'items' in data['error'] and 'quantity' in data['error']['items']['0']
    assert '库存不足' in str(data['error']), "Error message should indicate insufficient stock"

    # 验证库存未被错误扣减
    with client.application.app_context():
        book_after_fail = db.session.get(Book, book_fixture.id)
        assert book_after_fail.quantity == low_stock_quantity


def test_get_sales(client, admin_token):
    """测试获取销售记录列表"""
    # 发送请求
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/sales', headers=headers)

    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)

    assert 'sales' in data
    assert 'pagination' in data


def test_refund_sale(client, admin_token, book_fixture):
    """测试销售退款"""
    set_quantity = 20  # 测试设置的库存量
    sale_quantity = 2  # 销售数量
    expected_after_sale = set_quantity - sale_quantity  # 销售后预期库存 (18)
    expected_after_refund = set_quantity # 退款后预期库存 (20)

    # 首先设置初始库存并创建一笔销售
    with client.application.app_context():
        # 使用 session.get 获取书籍
        book = db.session.get(Book, book_fixture.id)
        assert book is not None, f"Book with ID {book_fixture.id} not found."
        book.quantity = set_quantity
        db.session.commit()
        print(f"\n[test_refund_sale] Quantity set to: {book.quantity}") # Debug

    # 创建销售数据
    sale_data = {
        'customer_name': '测试顾客',
        'contact': '13800138000',
        'payment_method': 'CASH',
        'remarks': '测试销售备注',
        'items': [
            {
                'book_id': book_fixture.id,
                'quantity': sale_quantity,
                'sale_price': float(book_fixture.retail_price)
            }
        ]
    }

    headers = {'Authorization': f'Bearer {admin_token}'}
    create_response = client.post('/api/sales', json=sale_data, headers=headers)
    assert create_response.status_code == 201, f"Sale creation failed: {create_response.data.decode('utf-8')}"
    create_data = json.loads(create_response.data)
    sale_id = create_data['id']

    # 验证销售后库存是否正确减少
    with client.application.app_context():
        book_after_sale = db.session.get(Book, book_fixture.id)
        print(f"[test_refund_sale] Quantity after sale: {book_after_sale.quantity}") # Debug
        assert book_after_sale.quantity == expected_after_sale, f"Stock not decreased correctly after sale. Expected {expected_after_sale}, got {book_after_sale.quantity}"

    # 进行退款
    refund_response = client.post(f'/api/sales/{sale_id}/refund', headers=headers)

    # 验证退款响应
    print(f"[test_refund_sale] Refund response status: {refund_response.status_code}") # Debug
    # print(f"[test_refund_sale] Refund response data: {refund_response.data.decode('utf-8')}") # Debug
    assert refund_response.status_code == 200, f"Refund request failed: {refund_response.data.decode('utf-8')}"
    refund_data = json.loads(refund_response.data)

    assert 'message' in refund_data
    assert refund_data['sale']['status'] == SALE_STATUS['REFUNDED']

    # 验证库存已恢复
    with client.application.app_context():
        book_after_refund = db.session.get(Book, book_fixture.id)
        print(f"[test_refund_sale] Quantity after refund: {book_after_refund.quantity}") # Debug
        assert book_after_refund.quantity == expected_after_refund, f"Stock not restored correctly after refund. Expected {expected_after_refund}, got {book_after_refund.quantity}"