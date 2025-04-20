# filepath: c:\Users\Elio\Desktop\book-management-system\bookstore_system\backend\wsgi.py
import os
from app import create_app
from dotenv import load_dotenv # <--- 添加这一行

# 从环境变量 FLASK_CONFIG 或默认值创建应用实例
# 加载 .env 文件 (如果存在)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, encoding='utf-8') # <--- 指定编码为 utf-8

# 优先使用 FLASK_CONFIG，其次 FLASK_ENV，最后默认为 'development'
# 确保 'development' 是 config.py 中有效的键
config_name = os.getenv('FLASK_CONFIG') or os.getenv('FLASK_ENV') or 'development'
app = create_app(config_name)

if __name__ == "__main__":
    # 这部分通常只在直接运行 wsgi.py 时执行 (不推荐用于生产)
    # 生产环境应使用 Gunicorn 或 uWSGI 等 WSGI 服务器
    app.run()# WSGI 应用入口
