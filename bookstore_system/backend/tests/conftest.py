import pytest
from app.models.user import User
from app.utils.auth import generate_token
from app import create_app, db as _db # Import create_app and db

print("conftest.py 被加载!")  # 添加此行以确认文件被加载

try:
    from app.models.user import User
    print("Successfully imported User model")
except ImportError as e:
    print(f"Error importing User model: {e}")

try:
    from app.utils.auth import generate_token
    print("Successfully imported generate_token")
except ImportError as e:
    print(f"Error importing generate_token: {e}")

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    # Ensure you are using a test configuration
    _app = create_app('testing') 
    
    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app # The tests will run with the app context

    ctx.pop()

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()

@pytest.fixture(scope='function')
def init_database(db):
    """Function-scoped database initialization."""
    # Clean up tables before each test
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    yield db
    # Clean up after test if needed, though session scope might handle it
    db.session.remove()

@pytest.fixture(scope='function') # Or 'session' if the admin user can persist
def admin_token(app, init_database): # Use init_database for a clean state if needed
    """Creates an admin user and returns an auth token."""
    print("\n>>> 执行 admin_token fixture")
    # Check if admin already exists to avoid duplicates if scope is session
    admin = init_database.session.query(User).filter_by(username='testadmin').first()
    print(f">>> 现有管理员用户: {admin}")
    if not admin:
        print(">>> 创建新管理员用户")
        admin = User(
            username='testadmin', 
            employee_id='ADM001', 
            role='SUPER_ADMIN',
            full_name='Test Admin'
        )
        admin.set_password('adminpass')
        init_database.session.add(admin)
        init_database.session.commit()
        print(f">>> 新管理员ID: {admin.id}")
    
    # Generate token within app context
    with app.app_context():
        print(">>> 在app上下文中生成token")
        token = generate_token(admin.id, admin.role)
        print(f">>> 生成的token: {token[:10]}...")
    return token

@pytest.fixture(scope='function')
def book_fixture(init_database):
    """Creates a sample book for testing."""
    from app.models.book import Book # Import inside fixture if needed
    book = Book(
        isbn='9781234567890', 
        name='测试用书', 
        author='测试作者', 
        publisher='测试出版社', 
        retail_price=50.00, 
        quantity=100 # Initial quantity
    )
    init_database.session.add(book)
    init_database.session.commit()
    return book

@pytest.fixture
def client(app):
    """Creates a test client for the Flask application."""
    return app.test_client()

