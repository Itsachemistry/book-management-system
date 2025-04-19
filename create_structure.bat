@echo off
echo 正在创建书店管理系统项目架构...

REM 创建项目主目录
mkdir bookstore_system
cd bookstore_system

REM 创建后端目录结构
mkdir backend
cd backend
mkdir app
cd app
mkdir models routes schemas services utils
echo. > __init__.py
echo. > database.py
echo. > config.py
echo. > constants.py

cd models
echo. > __init__.py
echo. > user.py
echo. > book.py
echo. > purchase_order.py
echo. > sale.py
echo. > transaction.py
echo. > base.py
cd ..

cd routes
echo. > __init__.py
echo. > auth_routes.py
echo. > user_routes.py
echo. > book_routes.py
echo. > procurement_routes.py
echo. > sales_routes.py
echo. > finance_routes.py
cd ..

cd schemas
echo. > __init__.py
echo. > user_schema.py
echo. > book_schema.py
cd ..

cd services
echo. > __init__.py
echo. > auth_service.py
echo. > user_service.py
echo. > book_service.py
echo. > procurement_service.py
echo. > sales_service.py
echo. > finance_service.py
cd ..

cd utils
echo. > __init__.py
echo. > auth.py
echo. > decorators.py
echo. > error_handlers.py
cd ..

cd ..
mkdir migrations
mkdir tests
cd tests
echo. > __init__.py
echo. > conftest.py
echo. > test_auth.py
echo. > test_users.py
cd ..

echo # 环境变量配置 > .env
echo FLASK_APP=wsgi.py > .flaskenv
echo # Python 项目依赖 > requirements.txt
echo # WSGI 应用入口点 > wsgi.py
echo # 后端说明文档 > README.md

cd ..

REM 创建前端目录结构
mkdir frontend
cd frontend
mkdir public src tests
cd public
echo. > index.html
cd ..

cd src
mkdir api assets components router store views
cd api
echo. > index.js
echo. > auth.js
echo. > users.js
echo. > books.js
cd ..

cd components
echo. > UserForm.vue
echo. > BookTable.vue
cd ..

cd router
echo. > index.js
cd ..

cd store
echo. > index.js
echo. > auth.js
echo. > user.js
echo. > book.js
cd ..

cd views
echo. > LoginView.vue
echo. > DashboardView.vue
echo. > UserManagementView.vue
echo. > BookInventoryView.vue
echo. > ProcurementView.vue
echo. > SalesView.vue
echo. > FinanceReportView.vue
echo. > NotFoundView.vue
cd ..

echo. > App.vue
echo. > main.js
cd ..

echo # 开发环境配置 > .env.development
echo # 生产环境配置 > .env.production
echo { "name": "bookstore-frontend" } > package.json
echo {} > package-lock.json
echo # 前端说明文档 > README.md

cd ..

REM 创建根目录其他文件
mkdir data
mkdir docs
echo # Git忽略文件 > .gitignore
echo # 项目许可证 > LICENSE

echo 文件架构创建完成！
