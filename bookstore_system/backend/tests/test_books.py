import pytest
import json
from app.models.user import User
from app.models.book import Book
from app.utils.auth import generate_token

@pytest.fixture
def create_admin_and_token(client, init_database, app):
    """创建管理员用户并生成token"""
    admin = User(username='admin', employee_id='ADMIN1', role='SUPER_ADMIN')
    admin.set_password('admin123')
    init_database.session.add(admin)
    init_database.session.commit()
    
    with app.app_context():
        token = generate_token(admin.id, admin.role)
    
    return admin, token

@pytest.fixture
def create_normal_user_and_token(client, init_database, app):
    """创建普通用户并生成token"""
    user = User(username='normaluser', employee_id='EMP301', role='NORMAL_ADMIN')
    user.set_password('password123')
    init_database.session.add(user)
    init_database.session.commit()
    
    with app.app_context():
        token = generate_token(user.id, user.role)
    
    return user, token

@pytest.fixture
def create_sample_books(init_database):
    """创建示例书籍数据"""
    books = [
        Book(
            isbn='9787302275954',
            name='Python编程：从入门到实践',
            author='埃里克·马瑟斯',
            publisher='人民邮电出版社',
            retail_price=59.00,
            quantity=100
        ),
        Book(
            isbn='9787115546081',
            name='流畅的Python',
            author='卢西亚诺·拉马略',
            publisher='人民邮电出版社',
            retail_price=139.00,
            quantity=50
        ),
        Book(
            isbn='9787111616054',
            name='JavaScript高级程序设计',
            author='Nicholas C. Zakas',
            publisher='机械工业出版社',
            retail_price=129.00,
            quantity=80
        )
    ]
    
    for book in books:
        init_database.session.add(book)
    
    init_database.session.commit()
    return books

def test_get_books_list(client, init_database, app):
    """测试获取书籍列表"""
    # 创建测试用户
    user = User(username='testuser', employee_id='EMP100')
    user.set_password('password123')
    init_database.session.add(user)
    
    # 创建测试书籍
    book1 = Book(isbn='1234567890', name='测试书籍1', author='测试作者1', 
                publisher='测试出版社', retail_price=29.99, quantity=10)
    book2 = Book(isbn='0987654321', name='测试书籍2', author='测试作者2', 
                publisher='测试出版社', retail_price=39.99, quantity=5)
    
    init_database.session.add_all([book1, book2])
    init_database.session.commit()
    
    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(user.id, user.role)
    
    # 请求书籍列表
    response = client.get('/api/books/',
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'books' in data
    assert len(data['books']) >= 2
    assert 'pagination' in data

def test_search_books(client, create_normal_user_and_token, create_sample_books):
    """测试搜索书籍功能"""
    _, token = create_normal_user_and_token
    
    # 按书名搜索
    response = client.get('/api/books/?search=Python',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['books']) == 2
    
    # 按作者搜索
    response = client.get('/api/books/?search=Zakas',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['books']) == 1

def test_get_book_detail(client, init_database, app):
    """测试获取单本书籍详情"""
    # 创建测试用户
    user = User(username='testuser', employee_id='EMP100')
    user.set_password('password123')
    init_database.session.add(user)
    
    # 创建测试书籍
    book = Book(isbn='1234567890', name='测试书籍1', author='测试作者1', 
               publisher='测试出版社', retail_price=29.99, quantity=10)
    
    init_database.session.add(book)
    init_database.session.commit()
    
    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(user.id, user.role)
    
    # 请求单本书籍详情
    response = client.get(f'/api/books/{book.id}',
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == book.id
    assert data['name'] == '测试书籍1'
    assert data['isbn'] == '1234567890'

def test_create_book(client, init_database, app):
    """测试创建书籍"""
    # 创建管理员用户
    admin = User(username='admin', employee_id='ADMIN1', role='SUPER_ADMIN')
    admin.set_password('admin123')
    init_database.session.add(admin)
    init_database.session.commit()
    
    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(admin.id, admin.role)
    
    # 书籍数据
    book_data = {
        'isbn': '9876543210',
        'name': '新书籍',
        'author': '新作者',
        'publisher': '新出版社',
        'retail_price': 49.99,
        'quantity': 20
    }
    
    # 发送请求创建书籍
    response = client.post('/api/books/',
                          data=json.dumps(book_data),
                          content_type='application/json',
                          headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['isbn'] == '9876543210'
    assert data['name'] == '新书籍'
    
    # 验证数据库中已保存
    book = Book.query.filter_by(isbn='9876543210').first()
    assert book is not None
    assert book.name == '新书籍'

def test_create_book_normal_user(client, create_normal_user_and_token):
    """测试普通用户无法创建书籍"""
    _, token = create_normal_user_and_token
    
    book_data = {
        "isbn": "9787115473288",
        "name": "测试书籍",
        "retail_price": 59.00,
        "quantity": 10
    }
    
    response = client.post('/api/books/',
                          data=json.dumps(book_data),
                          content_type='application/json',
                          headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应 - 应该返回403禁止访问
    assert response.status_code == 403

def test_update_book(client, init_database, app):
    """测试更新书籍"""
    # 创建管理员用户
    admin = User(username='admin', employee_id='ADMIN1', role='SUPER_ADMIN')
    admin.set_password('admin123')
    init_database.session.add(admin)
    
    # 创建测试书籍
    book = Book(isbn='1234567890', name='测试书籍', author='测试作者', 
               publisher='测试出版社', retail_price=29.99, quantity=10)
    
    init_database.session.add(book)
    init_database.session.commit()
    
    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(admin.id, admin.role)
    
    # 更新数据
    update_data = {
        'name': '更新后的书籍',
        'retail_price': 39.99,
        'quantity': 15
    }
    
    # 发送更新请求
    response = client.put(f'/api/books/{book.id}',
                         data=json.dumps(update_data),
                         content_type='application/json',
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == '更新后的书籍'
    assert float(data['retail_price']) == 39.99
    assert data['quantity'] == 15
    
    # 验证数据库中已更新
    updated_book = Book.query.get(book.id)
    assert updated_book.name == '更新后的书籍'
    assert float(updated_book.retail_price) == 39.99
    assert updated_book.quantity == 15

def test_delete_book(client, init_database, app):
    """测试逻辑删除书籍"""
    # 创建管理员用户
    admin = User(username='admin', employee_id='ADMIN1', role='SUPER_ADMIN')
    admin.set_password('admin123')
    init_database.session.add(admin)
    
    # 创建测试书籍
    book = Book(isbn='1234567890', name='测试书籍', author='测试作者', 
               publisher='测试出版社', retail_price=29.99, quantity=10)
    
    init_database.session.add(book)
    init_database.session.commit()
    
    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(admin.id, admin.role)
    
    # 发送删除请求
    response = client.delete(f'/api/books/{book.id}',
                            headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库中已标记为非活动
    deleted_book = Book.query.get(book.id)
    assert deleted_book is not None  # 仍然存在于数据库中
    assert deleted_book.is_active is False  # 但被标记为非活动

def test_normal_user_cannot_modify_books(client, init_database, app):
    """测试普通用户无法修改书籍"""
    # 创建普通用户
    user = User(username='normaluser', employee_id='EMP301', role='NORMAL_ADMIN')
    user.set_password('pass123')
    init_database.session.add(user)
    
    # 创建测试书籍
    book = Book(isbn='1234567890', name='测试书籍', author='测试作者', 
               publisher='测试出版社', retail_price=29.99, quantity=10)
    
    init_database.session.add(book)
    init_database.session.commit()
    
    # 在应用上下文中生成令牌
    with app.app_context():
        token = generate_token(user.id, user.role)
    
    # 尝试更新书籍
    update_data = {
        'name': '普通用户更新书籍',
        'retail_price': 19.99,
        'quantity': 5
    }
    
    response = client.put(f'/api/books/{book.id}',
                         data=json.dumps(update_data),
                         content_type='application/json',
                         headers={'Authorization': f'Bearer {token}'})
    
    # 验证响应 - 应该返回403禁止访问
    assert response.status_code == 403