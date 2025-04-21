from flask import Flask, request, jsonify
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
    ma.init_app(app)       # 关联 Marshmallow 到 app

    # 配置CORS - 确保允许来自前端的请求，包括localhost:3000和file://协议
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5174", 
                "http://127.0.0.1:5174", 
                "http://localhost:3000", 
                "http://127.0.0.1:3000",
                "file://", 
                "null"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "X-Total-Count"]
        }
    })
    CORS(app, supports_credentials=True)

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
    
    # 添加API根路由响应
    @app.route('/api', methods=['GET', 'OPTIONS'])
    def api_root():
        if request.method == 'OPTIONS':
            return '', 204
        return jsonify({"message": "欢迎使用书店管理系统API", "status": "online"})

    return app
