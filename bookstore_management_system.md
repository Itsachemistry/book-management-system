# 书店管理系统 - 文件架构说明

此文件包含了完整的书店管理系统项目架构。按照以下步骤使用：

1. 使用提供的脚本创建全部目录和空文件
2. 设置后端环境：
   - 进入 backend 目录
   - 安装依赖: `pip install -r requirements.txt`
   - 配置环境变量（.env 和 .flaskenv）
   
3. 设置前端环境：
   - 进入 frontend 目录
   - 安装依赖: `npm install` 或 `yarn`
   - 启动开发服务器: `npm run dev` 或 `yarn dev`

项目结构包含完整的后端（Flask）和前端（Vue.js）架构，符合现代全栈应用最佳实践。

好的，我已经仔细检查过，之前为您提供的**分任务列表**与**优化后的项目文件层次结构**是**完全吻合**的。每个任务都明确指向了文件结构中对应的文件或目录路径。

现在，我将这两部分再次分别输出给您，方便您对照参考。

-----

**一、优化后的项目文件层次结构**

```
your_project_name/
├── backend/                     # 后端代码 (Flask)
│   ├── app/                     # 将核心应用逻辑封装在一个包内
│   │   ├── __init__.py          # 应用工厂函数，创建 Flask app 实例，注册蓝图、扩展等
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── book.py
│   │   │   ├── purchase_order.py # 进货单模型 (示例命名)
│   │   │   ├── sale.py           # 销售记录模型 (示例命名)
│   │   │   └── transaction.py    # 财务流水模型 (示例命名)
│   │   │   └── base.py           # (可选) Base model or common mixins
│   │   ├── routes/              # API 路由 (Flask Blueprints)
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py    # 认证相关路由
│   │   │   ├── user_routes.py    # 用户管理路由
│   │   │   ├── book_routes.py    # 库存书籍管理路由
│   │   │   ├── procurement_routes.py # 进货流程路由
│   │   │   ├── sales_routes.py   # 销售路由
│   │   │   └── finance_routes.py # 财务路由
│   │   ├── schemas/             # (推荐) 数据序列化/反序列化 (e.g., Marshmallow schemas)
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py
│   │   │   ├── book_schema.py
│   │   │   └── ...
│   │   ├── services/            # (推荐) 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── book_service.py
│   │   │   ├── procurement_service.py
│   │   │   ├── sales_service.py
│   │   │   └── finance_service.py
│   │   ├── utils/               # 通用工具函数
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # JWT/密码哈希 (bcrypt)
│   │   │   ├── decorators.py    # (可选) 自定义装饰器 (权限检查)
│   │   │   └── error_handlers.py # (可选) 自定义错误处理
│   │   ├── database.py          # 数据库连接和会话管理 (SQLAlchemy setup)
│   │   ├── config.py            # 应用程序配置
│   │   └── constants.py         # (可选) 定义常量
│   ├── migrations/              # 数据库迁移脚本 (Alembic)
│   ├── tests/                   # 后端测试代码 (pytest)
│   │   ├── __init__.py
│   │   ├── conftest.py          # pytest 配置文件和 fixtures
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   └── ...
│   ├── .env                     # 环境变量文件 (数据库密码、密钥等 - **不提交到 Git**)
│   ├── .flaskenv                # Flask CLI 环境变量
│   ├── requirements.txt         # Python 依赖包列表
│   ├── wsgi.py                  # WSGI 入口点 (用于 Gunicorn/uWSGI 部署)
│   └── README.md
├── frontend/                    # 前端代码 (Vue.js)
│   ├── public/
│   │   └── index.html           # HTML 入口
│   │   └── ...
│   ├── src/
│   │   ├── api/                 # (推荐) 封装对后端 API 的请求
│   │   │   ├── index.js         # axios 实例配置, 拦截器等
│   │   │   ├── auth.js
│   │   │   ├── users.js
│   │   │   ├── books.js
│   │   │   └── ...
│   │   ├── assets/
│   │   ├── components/          # 可复用 UI 组件
│   │   │   ├── UserForm.vue
│   │   │   ├── BookTable.vue
│   │   │   └── ...
│   │   ├── router/              # Vue Router 配置
│   │   │   └── index.js         # 路由定义, 路由守卫
│   │   ├── store/               # 状态管理 (Pinia 推荐)
│   │   │   ├── index.js         # Pinia 实例
│   │   │   ├── auth.js          # 用户认证状态 store
│   │   │   ├── user.js          # 用户信息 store
│   │   │   ├── book.js          # 书籍数据 store
│   │   │   └── ...
│   │   ├── views/               # 页面级组件
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── UserManagementView.vue
│   │   │   ├── BookInventoryView.vue
│   │   │   ├── ProcurementView.vue
│   │   │   ├── SalesView.vue
│   │   │   ├── FinanceReportView.vue
│   │   │   └── NotFoundView.vue
│   │   ├── App.vue
│   │   └── main.js              # Vue 应用入口
│   ├── tests/                   # 前端测试 (e.g., Vitest/Jest + Vue Test Utils)
│   ├── .env.development         # 开发环境变量 (e.g., VITE_API_BASE_URL)
│   ├── .env.production          # 生产环境变量
│   ├── package.json
│   ├── package-lock.json / yarn.lock
│   └── README.md
├── data/                        # (可选) 存放初始化数据脚本、测试数据等
├── docs/                        # (可选) 项目文档 (API 文档、设计文档等)
├── .gitignore                   # Git 忽略文件
└── LICENSE
```

-----

**二、项目任务分解 (Copilot 友好版 - 中文)**

**(阶段 0: 环境搭建与基础设置 - 主要手动, AI 可辅助)**

  * **任务 0.1 (手动):** 设置 Git 仓库、Python 虚拟环境、Node 环境、PostgreSQL 数据库/用户。
  * **任务 0.2 (Copilot):** "为一个使用 Flask、Flask-SQLAlchemy、Flask-Migrate、psycopg2-binary、python-dotenv、Flask-Bcrypt、PyJWT、Flask-Cors、Flask-Marshmallow (或 Pydantic)、marshmallow-sqlalchemy 的 Flask 项目生成标准的 `requirements.txt` 文件内容。"
  * **任务 0.3 (Copilot):** "在 `backend/app/__init__.py` 中，创建一个 Flask 应用工厂函数 `create_app(config_name)`。该函数应初始化 Flask 应用，从 `config.py` 加载配置，初始化扩展 (db, migrate, bcrypt, cors, ma)，并返回 app 实例。包含基本的 CORS 设置。"
  * **任务 0.4 (Copilot):** "在 `backend/app/database.py` 中，初始化 Flask-SQLAlchemy (`db = SQLAlchemy()`) 和 Flask-Migrate (`migrate = Migrate()`)。"
  * **任务 0.5 (Copilot):** "在 `backend/app/config.py` 中，创建基础 `Config` 类以及子类 `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`。包含通用配置 (如从环境变量读取 SECRET\_KEY, SQLALCHEMY\_DATABASE\_URI) 和特定环境配置 (如 Development 的 DEBUG=True)。"
  * **任务 0.6 (Copilot):** "生成标准的 Python `.gitignore` 文件，包含 `venv`, `__pycache__`, `.env`, `instance` 等条目。同时添加 Node.js 相关条目，如 `node_modules`, `.DS_Store`。"
  * **任务 0.7 (手动/Copilot):** 使用 Vite (`npm create vite@latest`) 或 Vue CLI (`vue create`) 初始化前端项目。Copilot 可以提供命令和选项建议。
  * **任务 0.8 (Copilot):** "在 `frontend/src/main.js` 中，设置 Pinia 用于状态管理。"
  * **任务 0.9 (Copilot):** "在 `frontend/src/router/index.js` 中，设置基础的 Vue Router，包含几个占位路由 (例如 '/', '/login')。"
  * **任务 0.10 (Copilot):** "在 `frontend/src/api/index.js` 中，创建并配置一个 Axios 实例。根据 `import.meta.env.VITE_API_BASE_URL` 设置 `baseURL`。如果后续需要（例如添加认证令牌），可以添加请求/响应拦截器。"
  * **任务 0.11 (手动):** 在共享文档中定义初始的 API 约定（登录、获取书籍列表）。

**(阶段 1: 用户管理与认证)**

  * **后端:**
      * **任务 1.1 (Copilot):** "在 `backend/app/models/user.py` 中，按指定要求 [包含列：id(整数,主键), username(字符串80,唯一,非空), hashed\_password(字符串128,非空), full\_name(字符串100), employee\_id(字符串50,唯一,非空), gender(字符串10), age(整数), role(字符串20,默认'NORMAL\_ADMIN',非空)] 创建 `User` SQLAlchemy 模型。包含使用 Flask-Bcrypt (或直接用 bcrypt) 的 `set_password` 和 `check_password` 方法。" *上下文: 导入 `db` from `..database`, `bcrypt`.*
      * **任务 1.2 (Copilot):** "在 `backend/app/schemas/user_schema.py` 中，创建 Marshmallow Schemas: `UserSchema` (排除密码字段), `UserRegistrationSchema` (用户名, 密码, 必填字段), `LoginSchema` (用户名, 密码)。" *上下文: 导入 `User` 模型, `ma` (Marshmallow 实例).*
      * **任务 1.3 (Copilot):** "在 `backend/app/utils/auth.py` 中，创建函数 `generate_token(user_id, role)` 和 `verify_token(token)`，使用 PyJWT 和应用的 SECRET\_KEY。" *上下文: 导入 `jwt`, `current_app`.*
      * **任务 1.4 (Copilot):** "在 `backend/app/utils/decorators.py` 中，创建一个 `@login_required` 装饰器。它应从 'Authorization: Bearer \<token\>' 请求头获取 token，使用 `utils.auth.verify_token` 验证，查找用户，将用户信息附加到 `flask.g.user`，并在无效时返回 401。创建 `@admin_required` 装饰器，检查 `g.user.role == 'SUPER_ADMIN'`。" *上下文: 导入 `functools`, `request`, `abort`, `g`, `verify_token`, `User` 模型.*
      * **任务 1.5 (Copilot):** "在 `backend/app/routes/auth_routes.py` 中，创建一个 Flask Blueprint `auth_bp`。实现 `POST /login` 路由：使用 `LoginSchema` 反序列化请求，查找用户，使用 `user.check_password` 校验密码，使用 `utils.auth.generate_token` 生成 JWT，返回 `{'token': ..., 'user': ...}` (序列化后的用户信息)。" *上下文: 导入 Blueprint, request, jsonify, schemas, models, utils.*
      * **任务 1.6 (Copilot):** "在 `auth_routes.py` 中，实现 `GET /me` 路由：使用 `@login_required` 保护，返回使用 `UserSchema` 序列化后的 `g.user`。" *上下文: 导入 `@login_required`, `g`, `UserSchema`.*
      * **任务 1.7 (Copilot):** "在 `backend/app/routes/user_routes.py` 中，创建一个 Blueprint `user_bp`。实现 `POST /` 路由：使用 `@admin_required` 保护，使用 `UserRegistrationSchema` 反序列化请求，创建 `User` 实例（哈希密码），添加到数据库 session，提交，返回创建的用户（序列化后）。"
      * **任务 1.8 (Copilot):** "在 `user_routes.py` 中，实现 `GET /` 路由：使用 `@admin_required` 保护，查询所有用户，返回使用 `UserSchema(many=True)` 序列化的列表。"
      * **任务 1.9 (Copilot):** "在 `user_routes.py` 中，实现 `PUT /me` 路由：使用 `@login_required` 保护，反序列化请求（允许更新特定字段如 full\_name, age），更新 `g.user`，提交，返回更新后的用户。"
      * **任务 1.10 (手动/Copilot):** 在 `backend/app/__init__.py` 中，在应用工厂函数里注册 `auth_bp` 和 `user_bp` 这两个 Blueprint。
      * **任务 1.11 (手动/Copilot):** 设置 Flask-Migrate: 运行 `flask db init` (首次), `flask db migrate -m "Add User model"`, `flask db upgrade`。创建一个 Flask CLI 命令或脚本来初始化（seed）第一个超级管理员用户。
      * **任务 1.12 (Copilot):** "在 `backend/tests/test_auth.py` 中，使用测试客户端为 `/login` 和 `/me` 端点编写 pytest 测试。测试成功登录、无效凭证、带/不带 token 访问 `/me` 的情况。" *上下文: 需要 Flask app fixture (`client`).*
      * **任务 1.13 (Copilot):** "在 `backend/tests/test_users.py` 中，编写 pytest 测试，覆盖管理员创建用户、管理员列出用户、非管理员访问被阻止、用户更新自己的个人资料等场景。"
  * **前端:**
      * **任务 1.14 (Copilot):** "在 `frontend/src/api/auth.js` 中，创建异步函数 `login(credentials)` 和 `WorkspaceCurrentUser()`。使用配置好的 Axios 实例调用 `POST /api/auth/login` 和 `GET /api/auth/me`。包含错误处理。"
      * **任务 1.15 (Copilot):** "在 `frontend/src/store/auth.js` (Pinia) 中：定义 state (`token`, `user`, `status`)。定义 actions: `login(credentials)` (调用 API，在 state 和 localStorage 中存储 token/user，更新 status，返回 user)， `logout` (清除 state/localStorage)， `WorkspaceUser` (调用 API 更新 state)， `initialize` (应用加载时检查 localStorage)。" *上下文: 导入 API 函数, router.*
      * **任务 1.16 (Copilot):** "在 `frontend/src/views/LoginView.vue` 中：创建一个包含用户名和密码输入框（使用 `v-model`）的表单。提交时调用 `authStore.login()` action。处理加载状态并显示错误信息。成功后使用 `vue-router` 重定向到仪表板。" *上下文: 使用 Pinia (`useAuthStore`), Vue Router (`useRouter`).*
      * **任务 1.17 (Copilot):** "在 `frontend/src/router/index.js` 中：添加导航守卫 (`router.beforeEach`)。检查 `authStore.token`。如果路由的 `meta.requiresAuth` 为 true 且 token 不存在，则重定向到 '/login'。如果目标是 '/login' 但用户已登录，则重定向到 '/'。" *上下文: 在守卫内部导入 `useAuthStore`.*
      * **任务 1.18 (Copilot):** "在 `frontend/src/main.js` 或 `App.vue` 中，确保应用启动时调用 `authStore.initialize()` action。"
      * **任务 1.19 (Copilot):** "在 `frontend/src/api/users.js` 中：创建函数 `createUser(userData)`, `getUsers()`, `updateProfile(profileData)`，调用相应的后端用户管理端点。"
      * **任务 1.20 (Copilot):** "在 `frontend/src/views/UserManagementView.vue` 中：如果用户是管理员 (检查 `authStore.user.role`)，则使用 `usersApi.getUsers()` 获取用户列表并显示在表格中。添加按钮/模态框以触发使用 `usersApi.createUser()` 创建用户。"
      * **任务 1.21 (Copilot):** "创建 `frontend/src/views/ProfileView.vue`：获取当前用户信息 (`authStore.user` 或调用 `/api/auth/me`)。显示用户信息并提供表单以更新允许的字段，调用 `usersApi.updateProfile()`。"

**(阶段 2: 库存书籍管理 - CRUD)**

  * **后端:**
      * 任务 2.1 (Copilot): 创建 `Book` 模型 (`models/book.py`) - ISBN (主键或唯一键), name, publisher, author, retail\_price (Numeric/Float), quantity (整数)。
      * 任务 2.2 (Copilot): 创建 `BookSchema` (`schemas/book_schema.py`)。
      * 任务 2.3 (Copilot): 创建 `book_bp` (`routes/book_routes.py`)。实现 `GET /` (列出书籍，添加查询参数用于按书名/作者/ISBN 搜索，支持分页)。
      * 任务 2.4 (Copilot): 在 `book_bp` 中实现 `GET /<isbn_or_id>`。
      * 任务 2.5 (Copilot): 在 `book_bp` 中实现 `POST /` (添加书籍，可能需要管理员权限)。
      * 任务 2.6 (Copilot): 在 `book_bp` 中实现 `PUT /<isbn_or_id>` (更新书籍，可能需要管理员权限)。
      * 任务 2.7 (Copilot): 在 `book_bp` 中实现 `DELETE /<isbn_or_id>` (可选，考虑通过在模型中添加 `is_active` 标记来实现逻辑删除)。
      * 任务 2.8 (Copilot): 编写测试 (`tests/test_books.py`)。
      * 任务 2.9 (手动/Copilot): 运行数据库迁移。注册 Blueprint。
  * **前端:**
      * 任务 2.10 (Copilot): 创建 API 函数 (`api/books.js`) - getBooks(params), getBook(id), createBook(data), updateBook(id, data), deleteBook(id)。
      * 任务 2.11 (Copilot): 创建 Pinia store 切片 (`store/book.js`) - 管理书籍列表、当前书籍、加载状态。
      * 任务 2.12 (Copilot): 创建 `BookInventoryView.vue` 视图。
      * 任务 2.13 (Copilot): 创建 `BookTable.vue` 组件 (props: books 列表)。
      * 任务 2.14 (Copilot): 创建 `BookForm.vue` 组件 (用于添加/编辑，触发 save 事件)。
      * 任务 2.15 (Copilot): 创建搜索/过滤组件。将这些组件整合到 `BookInventoryView` 中。

**(阶段 3: 图书进货流程)**

  * **后端:**
      * 任务 3.1: 创建模型 `PurchaseOrder`, `PurchaseOrderItem` (`models/`)。关联 User, Book。包含 status ('UNPAID', 'PAID', 'RETURNED'), purchase\_price, quantity 等字段。
      * 任务 3.2: 创建 Schemas (`schemas/`)。
      * 任务 3.3: 创建路由 (`procurement_routes.py`) - 创建进货单 (`POST /orders`)。
      * 任务 3.4: 创建路由 - 列出进货单 (`GET /orders`, 按状态过滤)。
      * 任务 3.5: 创建路由 - 进货付款 (`POST /orders/<id>/pay`)。*逻辑: 更新订单状态, 创建 'EXPENSE' 类型的财务记录。*
      * 任务 3.6: 创建路由 - 进货退货 (`POST /orders/<id>/return`)。*逻辑: 仅当状态为 'UNPAID' 时更新为 'RETURNED'。*
      * 任务 3.7: 创建路由 - 图书入库 (`POST /orders/<id>/stock-in`)。*逻辑: 仅当状态为 'PAID' 时执行，增加/更新 Book 的库存数量，可能需要设置零售价。*
      * 任务 3.8: 编写测试 (`tests/`)。
      * 任务 3.9: 运行迁移，注册 Blueprint。
  * **前端:**
      * 任务 3.10: 创建 API 函数 (`api/procurement.js`)。
      * 任务 3.11: 创建 Store 切片 (`store/procurement.js`)。
      * 任务 3.12: 创建视图 (`ProcurementView.vue`) - 显示进货单列表，根据状态显示/禁用操作按钮。
      * 任务 3.13: 创建用于创建进货单的组件 (选择已有书籍或输入新书信息)。

**(阶段 4: 书籍销售与财务管理)**

  * **后端:**
      * 任务 4.1: 创建模型 `Sale`, `SaleItem`, `Transaction` (`models/`)。
      * 任务 4.2: 创建 Schemas (`schemas/`)。
      * 任务 4.3: 创建路由 (`sales_routes.py`) - 创建销售记录 (`POST /sales`)。*逻辑: 检查库存，减少 Book 库存，创建 Sale 记录，创建 'INCOME' 类型的财务记录。*
      * 任务 4.4: 创建路由 (`finance_routes.py`) - 查询财务记录 (`GET /transactions`, 按日期范围、类型过滤)。
      * 任务 4.5: 编写测试 (`tests/`)。
      * 任务 4.6: 运行迁移，注册 Blueprints。
  * **前端:**
      * 任务 4.7: 创建 API 函数 (`api/sales.js`, `api/finance.js`)。
      * 任务 4.8: 创建 Store 切片 (`store/sales.js`, `store/finance.js`)。
      * 任务 4.9: 创建视图 (`SalesView.vue`) - 选择书籍、数量，确认购买。
      * 任务 4.10: 创建视图 (`FinanceReportView.vue`) - 提供日期选择器，显示查询到的财务流水列表。

**(阶段 5: 完善、测试与文档)**

  * 任务 5.1 (Copilot): "为 `backend/app/routes/book_routes.py` 中的所有函数和类添加文档字符串 (docstrings)。" (对其余文件重复此操作)。
  * 任务 5.2 (Copilot): "为 `backend/app/routes/procurement_routes.py` 编写更全面的 pytest 测试，重点关注边界情况，例如尝试支付已支付订单或对未付款订单进行入库操作。"
  * 任务 5.3 (Copilot): "为后端项目生成基本的 `README.md` 文件，包含安装说明、运行开发服务器、运行测试和环境变量等部分。" (为前端项目重复此操作)。
  * 任务 5.4 (手动): 进行全面的手动测试，调试 Bug，优化 UI/UX。
