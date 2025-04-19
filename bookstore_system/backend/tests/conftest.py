import pytest
import os
from app import create_app, db

@pytest.fixture
def app():
    """创建并配置用于测试的Flask应用"""
    # 使用测试配置
    app = create_app('testing')
    
    # 创建测试上下文
    with app.app_context():
        # 创建数据库表
        db.create_all()
        yield app
        # 测试后清理
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """返回测试客户端"""
    return app.test_client()

@pytest.fixture
def init_database(app):
    """返回数据库实例以便在测试中使用"""
    return db

