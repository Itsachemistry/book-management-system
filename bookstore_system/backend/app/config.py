import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env')) # 加载 backend/.env

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string' # 用于 session、CSRF 等的安全密钥
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 关闭 SQLAlchemy 事件通知，节省资源
    # 可以在这里添加其他通用配置
    ITEMS_PER_PAGE = 20  # 分页默认值
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # JWT令牌过期时间(秒)
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'uploads')  # 文件上传目录

    @staticmethod
    def init_app(app):
        # 可以在这里执行应用级别的初始化操作
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True # 开启 Debug 模式
    # 开发环境数据库 URI (从 .env 文件读取)
    # 示例: postgresql://bookstore_user:your_password@localhost/bookstore_db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dev-db.sqlite') # 如果没有设置环境变量，使用 sqlite 作为备选

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True # 开启测试模式
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://' # 测试通常使用内存数据库或单独的测试数据库
    WTF_CSRF_ENABLED = False # 测试时通常禁用 CSRF 保护

class ProductionConfig(Config):
    """生产环境配置"""
    # 生产环境数据库 URI (从 .env 文件读取)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # 生产环境必须配置数据库 URL
    # 可以在这里添加生产环境特定的配置，例如日志级别、服务器名等

# 将配置名称映射到配置类
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # 默认使用开发环境配置
}

