from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_marshmallow import Marshmallow

# 从同级目录导入配置和数据库实例
from .config import config
from .database import db, migrate

# 初始化扩展，但不传入 app
bcrypt = Bcrypt()
cors = CORS()
ma = Marshmallow()

def create_app(config_name='development'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 1. 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) # 执行特定配置的初始化方法

    # 2. 初始化扩展
    db.init_app(app)       # 关联 SQLAlchemy 到 app
    migrate.init_app(app, db) # 关联 Migrate 到 app 和 db
    bcrypt.init_app(app)   # 关联 Bcrypt 到 app
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # 配置 CORS，允许所有来源访问 /api/ 下的路由 (开发时常用)
    ma.init_app(app)       # 关联 Marshmallow 到 app

    # 3. 注册蓝图 (Blueprints)
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from .routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # 添加书籍蓝图
    from .routes.book_routes import book_bp
    app.register_blueprint(book_bp, url_prefix='/api/books')
    
    # 添加采购蓝图
    from .routes.procurement_routes import procurement_bp
    app.register_blueprint(procurement_bp, url_prefix='/api/procurement')
    
    # 添加销售蓝图
    from .routes.sales_routes import sales_bp
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    
    # ... 其他蓝图将在后续阶段添加

    # 注册命令行命令
    from .commands import register_commands
    register_commands(app)

    return app

