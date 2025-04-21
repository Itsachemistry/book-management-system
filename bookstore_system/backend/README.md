# 书店管理系统 - 后端

这是书店管理系统的后端部分，使用 Flask 框架构建，提供完整的 RESTful API 接口。

## 功能特点

- 用户认证与授权
- 书籍库存管理
- 采购流程管理
- 销售记录管理
- 财务报表生成
- 完整的单元测试覆盖

## 技术栈

- **Web框架**: Flask
- **ORM**: SQLAlchemy
- **数据库迁移**: Flask-Migrate (Alembic)
- **数据库**: PostgreSQL
- **序列化/反序列化**: Marshmallow
- **认证**: JWT (PyJWT)
- **密码加密**: Flask-Bcrypt
- **CORS支持**: Flask-CORS
- **测试**: pytest

## 安装与设置

### 环境要求

- Python 3.8+ 
- PostgreSQL 13+

### 步骤

1. 克隆项目
   ```bash
   git clone <repository-url>
   cd book-management-system/bookstore_system/backend
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量

   创建 `.env` 文件并设置以下变量:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://username:password@localhost:5432/bookstore_db
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   ```

## 数据库设置

1. 创建数据库

   ```bash
   # 登录PostgreSQL
   psql -U postgres
   ```

   ```sql
   CREATE USER bookstoreuser WITH PASSWORD 'admin';
   CREATE DATABASE bookstore_db OWNER bookstoreuser;
   ```

2. 运行数据库迁移

   ```bash
   flask db upgrade
   ```

3. (可选) 初始化测试数据

   ```bash
   flask seed-db
   ```

## 运行应用

### 开发环境

```bash
flask run
```

访问 http://localhost:5000/api/ 

### 生产环境

```bash
gunicorn wsgi:app
```

## API文档

API端点按功能分组:

- `/api/auth/`: 认证相关 (登录, 当前用户信息)
- `/api/users/`: 用户管理
- `/api/books/`: 书籍管理
- `/api/procurement/`: 采购流程
- `/api/sales/`: 销售管理
- `/api/finance/`: 财务报表

详细API文档请参考 `/docs/api` 目录或项目上线后的API文档页面。

## 测试

```bash
pytest
```

指定测试文件或目录:

```bash
pytest tests/test_auth.py
```

带覆盖率报告:

```bash
pytest --cov=app tests/
```

## 目录结构
`
