import pytest
import json
from datetime import datetime, timedelta
from app.models.transaction import Transaction, TRANSACTION_TYPES
from app.utils.auth import generate_token


def test_get_transactions(client, admin_token):
    """测试获取财务记录列表"""
    # 发送请求
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/finance/transactions', headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'transactions' in data
    assert 'pagination' in data


def test_get_transactions_with_filters(client, admin_token):
    """测试使用过滤器获取财务记录"""
    # 设置过滤参数
    query_params = {
        'transaction_type': TRANSACTION_TYPES['INCOME'],
        'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    }
    
    # 发送请求
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/finance/transactions', query_string=query_params, headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证只返回了收入类型的交易
    for transaction in data['transactions']:
        assert transaction['transaction_type'] == TRANSACTION_TYPES['INCOME']


def test_get_summary(client, admin_token):
    """测试获取财务摘要"""
    # 发送请求
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/finance/summary', headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证包含所需字段
    assert 'total_income' in data
    assert 'total_expense' in data
    assert 'net_profit' in data
    assert 'today_income' in data
    assert 'month_income' in data
    assert 'by_type' in data


def test_access_control(client, normal_token):
    """测试非管理员访问限制"""
    # 使用普通用户令牌访问财务摘要
    headers = {'Authorization': f'Bearer {normal_token}'}
    response = client.get('/api/finance/summary', headers=headers)
    
    # 验证是否被拒绝访问
    assert response.status_code == 403