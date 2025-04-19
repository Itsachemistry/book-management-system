#!/bin/bash
echo "正在创建书店管理系统项目架构..."

# 创建项目主目录
mkdir -p bookstore_system
cd bookstore_system

# 创建后端目录结构
mkdir -p backend/app/{models,routes,schemas,services,utils}
mkdir -p backend/{migrations,tests}
touch backend/app/__init__.py
touch backend/app/{database.py,config.py,constants.py}

# 创建models文件
touch backend/app/models/{__init__.py,user.py,book.py,purchase_order.py,sale.py,transaction.py,base.py}

# 创建routes文件
touch backend/app/routes/{__init__.py,auth_routes.py,user_routes.py,book_routes.py,procurement_routes.py,sales_routes.py,finance_routes.py}

# 创建schemas文件
touch backend/app/schemas/{__init__.py,user_schema.py,book_schema.py}

# 创建services文件
touch backend/app/services/{__init__.py,auth_service.py,user_service.py,book_service.py,procurement_service.py,sales_service.py,finance_service.py}

# 创建utils文件
touch backend/app/utils/{__init__.py,auth.py,decorators.py,error_handlers.py}

# 创建测试文件
touch backend/tests/{__init__.py,conftest.py,test_auth.py,test_users.py}

# 创建后端根目录文件
echo "# 环境变量配置" > backend/.env
echo "FLASK_APP=wsgi.py" > backend/.flaskenv
echo "# Python 项目依赖" > backend/requirements.txt
echo "# WSGI 应用入口点" > backend/wsgi.py
echo "# 后端说明文档" > backend/README.md

# 创建前端目录结构
mkdir -p frontend/{public,src/{api,assets,components,router,store,views},tests}

# 创建public文件
touch frontend/public/index.html

# 创建src各模块文件
touch frontend/src/api/{index.js,auth.js,users.js,books.js}
touch frontend/src/components/{UserForm.vue,BookTable.vue}
touch frontend/src/router/index.js
touch frontend/src/store/{index.js,auth.js,user.js,book.js}
touch frontend/src/views/{LoginView.vue,DashboardView.vue,UserManagementView.vue,BookInventoryView.vue,ProcurementView.vue,SalesView.vue,FinanceReportView.vue,NotFoundView.vue}
touch frontend/src/{App.vue,main.js}

# 创建前端根目录文件
echo "# 开发环境配置" > frontend/.env.development
echo "# 生产环境配置" > frontend/.env.production
echo '{ "name": "bookstore-frontend" }' > frontend/package.json
echo "{}" > frontend/package-lock.json
echo "# 前端说明文档" > frontend/README.md

# 创建根目录其他文件
mkdir -p {data,docs}
echo "# Git忽略文件" > .gitignore
echo "# 项目许可证" > LICENSE

echo "文件架构创建完成！"
