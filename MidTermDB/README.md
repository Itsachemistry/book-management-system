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
```
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
- 书籍库存管理
- 采购管理
- 销售管理
- 财务报表
- 用户管理

## 目录结构说明

项目采用模块化结构，详细的目录结构见 `bookstore_management_system.md` 文件。
