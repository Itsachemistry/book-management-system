from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 创建 SQLAlchemy 实例，用于 ORM 操作
db = SQLAlchemy()
# 创建 Migrate 实例，用于数据库迁移
migrate = Migrate()

