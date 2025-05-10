# 书店管理系统

此项目是一个完整的书店管理系统，包含前端和后端代码，用于管理书籍库存、销售、采购和财务。

## 项目架构

项目采用前后端分离架构:
- **后端**: Flask (Python) + SQLAlchemy
- **前端**: Vue.js + Pinia

## 快速开始

### 使用自动化脚本创建项目结构:

**Windows用户**:
```
create_structure.bat
```

**Linux/Mac用户**:
```bash
chmod +x create_structure.sh
./create_structure.sh
```

### 启动开发环境

1. **后端设置**:
```bash
cd bookstore_system/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

2. **前端设置**:
```bash
cd bookstore_system/frontend
npm install
npm run dev
```

## 功能模块

- 用户认证与授权
  - 超级管理员：可管理所有用户账户，拥有所有系统权限
  - 普通管理员：不能管理用户账户，但可以管理书籍、采购、销售等业务功能
- 书籍库存管理
- 采购管理
- 销售管理
- 财务报表
- 用户管理（仅超级管理员可见）

## 目录结构说明

项目采用模块化结构，详细的目录结构见 `bookstore_management_system.md` 文件。

## 项目迁移指南

如需将项目迁移到新环境，请参考项目根目录下的 `MIGRATION_GUIDE.md` 文件，其中包含:

1. 数据库迁移步骤
2. 环境配置说明
3. 常见问题解决方案

迁移前请先执行数据库备份:
```bash
pg_dump -U bookstoreuser -d bookstore_db -f bookstore_backup.sql
```

新环境配置可使用自动化脚本:
- Windows: `setup_environment.bat`
- Linux/Mac: `setup_environment.sh`

## 如何将项目迁移到新环境

拿到本项目命名为 book-management-system的项目文件并解压之后，删除backend/venv文件夹。
使用代码中对数据表的定义脚本进行数据库创建，或者使用我们的数据库备份（带有一些模拟数据）恢复到你的数据库中即可。
确保本机已安装python的合适版本，安装node.js 这些需要在相应官网下载。

安装完毕后，进入backend目录，建立虚拟环境：
首先需要安装 virtualenv 包：
```bash
pip install virtualenv
```

然后创建虚拟环境：
```bash
cd backend
python -m venv venv
# 会生成一个venv目录
```

激活虚拟环境：
- Windows系统：
```bash
venv\Scripts\activate
```
- Linux/Mac系统：
```bash
source venv/bin/activate
```

安装项目依赖：
```bash
pip install -r requirements.txt
```

之后在前端安装依赖：
```bash
cd ../frontend
npm install
```

然后通过vscode将所有相关的路径修改成你存放项目代码的路径，
就可以使用start.bat启动文件项目。

## 数据库的建立过程

### 1. 创建PostgreSQL用户和数据库

```sql
-- 登录PostgreSQL
psql -U postgres

-- 创建用户和数据库
CREATE USER bookstoreuser WITH PASSWORD 'admin';
CREATE DATABASE bookstore_db OWNER bookstoreuser;
```

### 2. 模型定义

在代码库中，所有数据库表都是通过SQLAlchemy ORM模型定义的，主要位于models目录下：

#### 主要模型文件：

1. **用户表**：`user.py`
   ```python
   class User(db.Model):
       __tablename__ = 'users'
       id = db.Column(db.Integer, primary_key=True)
       username = db.Column(db.String(80), unique=True, nullable=False)
       hashed_password = db.Column(db.String(128), nullable=False)
       full_name = db.Column(db.String(100))
       employee_id = db.Column(db.String(50), unique=True, nullable=False)
       gender = db.Column(db.String(10))
       age = db.Column(db.Integer)
       role = db.Column(db.String(20), default='NORMAL_ADMIN', nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

2. **书籍表**：`book.py`
   ```python
   class Book(db.Model):
       __tablename__ = 'books'
       id = db.Column(db.Integer, primary_key=True)
       isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
       name = db.Column(db.String(200), nullable=False, index=True)
       author = db.Column(db.String(100))
       publisher = db.Column(db.String(100))
       publish_date = db.Column(db.Date)
       category = db.Column(db.String(50))
       description = db.Column(db.Text)
       retail_price = db.Column(db.Numeric(10, 2))
       quantity = db.Column(db.Integer, default=0)
       is_active = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

3. **采购订单表**：`purchase_order.py`
   ```python
   class PurchaseOrder(db.Model):
       __tablename__ = 'purchase_orders'
       id = db.Column(db.Integer, primary_key=True)
       order_number = db.Column(db.String(50), unique=True, nullable=False)
       supplier = db.Column(db.String(100), nullable=False)
       status = db.Column(db.String(20), default='UNPAID', nullable=False)
       order_date = db.Column(db.DateTime, default=datetime.utcnow)
       total_amount = db.Column(db.Numeric(10, 2), nullable=False)
       user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
       user = db.relationship('User', backref=db.backref('purchase_orders', lazy=True))
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
       
       items = db.relationship('PurchaseOrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
   
   class PurchaseOrderItem(db.Model):
       __tablename__ = 'purchase_order_items'
       id = db.Column(db.Integer, primary_key=True)
       purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
       isbn = db.Column(db.String(20), nullable=False)
       name = db.Column(db.String(200), nullable=False)
       quantity = db.Column(db.Integer, nullable=False)
       purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
       book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
       book = db.relationship('Book', backref=db.backref('purchase_items', lazy=True))
       subtotal = db.Column(db.Numeric(10, 2), nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

4. **销售表**：`sale.py`
   ```python
   class Sale(db.Model):
       __tablename__ = 'sales'
       id = db.Column(db.Integer, primary_key=True)
       sale_number = db.Column(db.String(50), unique=True, nullable=False)
       sale_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
       customer_name = db.Column(db.String(100))
       total_amount = db.Column(db.Numeric(10, 2), nullable=False)
       payment_method = db.Column(db.String(20), nullable=False)
       user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
       user = db.relationship('User', backref=db.backref('sales', lazy=True))
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
       
       items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
   
   class SaleItem(db.Model):
       __tablename__ = 'sale_items'
       id = db.Column(db.Integer, primary_key=True)
       sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
       book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
       book = db.relationship('Book', backref=db.backref('sale_items', lazy=True))
       quantity = db.Column(db.Integer, nullable=False)
       price = db.Column(db.Numeric(10, 2), nullable=False)
       subtotal = db.Column(db.Numeric(10, 2), nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

5. **财务交易表**：`transaction.py`
   ```python
   class Transaction(db.Model):
       __tablename__ = 'transactions'
       id = db.Column(db.Integer, primary_key=True)
       transaction_type = db.Column(db.String(20), nullable=False)  # INCOME, EXPENSE
       amount = db.Column(db.Numeric(10, 2), nullable=False)
       reference_id = db.Column(db.Integer)  # 关联的订单ID（销售或采购）
       reference_type = db.Column(db.String(20))  # SALE, PURCHASE
       description = db.Column(db.Text)
       transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
       created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
       user = db.relationship('User', backref=db.backref('transactions', lazy=True))
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

### 3. 数据库创建命令

然后，通过命令行指令创建这些表：

```bash
# 1. 首先创建PostgreSQL用户和空数据库
psql -U postgres
CREATE USER bookstoreuser WITH PASSWORD 'admin';
CREATE DATABASE bookstore_db OWNER bookstoreuser;

# 2. 初始化Flask-Migrate迁移仓库
flask db init

# 3. 创建迁移脚本（基于模型定义与当前数据库的差异）
flask db migrate -m "Initial migration"

# 4. 应用迁移，创建表结构
flask db upgrade

# 5. 创建管理员账户
flask init-admin --username admin --password admin123 --employee-id EMP001
```

或者，如果已经有备份文件，可以直接恢复：

```bash
psql -U bookstoreuser -d bookstore_db -f bookstore_backup.sql
```

### 4. 关键点

- 表的**结构**是通过Python代码中的SQLAlchemy模型定义的
- 实际的**表创建**是通过Flask-Migrate命令完成的，它会:
  1. 读取模型定义
  2. 生成SQL迁移脚本
  3. 应用这些SQL到数据库中

这种方法的优势在于可以通过代码管理数据库结构，并且可以跟踪数据库结构的变更历史。