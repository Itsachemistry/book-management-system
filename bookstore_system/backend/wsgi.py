# filepath: c:\Users\Elio\Desktop\book-management-system\bookstore_system\backend\wsgi.py
import os
from app import create_app

# 从环境变量 FLASK_CONFIG 或默认值创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == "__main__":
    # 这部分通常只在直接运行 wsgi.py 时执行 (不推荐用于生产)
    # 生产环境应使用 Gunicorn 或 uWSGI 等 WSGI 服务器
    app.run()# WSGI 应用入口�?
