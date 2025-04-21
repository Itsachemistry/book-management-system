# 书店管理系统 - 前端

这是书店管理系统的前端部分，基于Vue.js 3构建的现代化单页应用，提供完整的书店业务流程管理界面。

## 功能特点

- **用户管理与认证** - 基于角色的访问控制系统，区分普通管理员和超级管理员
- **书籍库存管理** - 添加、编辑、查询图书信息，追踪库存变化
- **采购流程管理** - 创建进货订单，跟踪订单状态（未支付、已支付、已入库、已退货）
- **销售管理** - 记录销售交易，支持退款操作
- **财务报表** - 可视化展示收入、支出和利润数据
- **响应式设计** - 适配不同设备屏幕尺寸

## 技术栈

- **Vue.js 3** - 核心前端框架，使用组合式API
- **Vue Router** - 客户端路由管理
- **Pinia** - 状态管理库，Vue官方推荐的Vuex替代品
- **Axios** - HTTP客户端，用于API请求
- **Vite** - 现代前端构建工具
- **CSS** - 自定义样式，包含响应式设计

## 安装与设置

### 环境要求

- Node.js 14+ 
- npm 6+ 或 yarn 1.22+

### 步骤

1. 克隆项目
   ```bash
   git clone <repository-url>
   cd book-management-system/bookstore_system/frontend
   ```

2. 安装依赖
   ```bash
   # 使用npm
   npm install
   
   # 或者使用yarn
   yarn
   ```

3. 配置环境变量

   创建 `.env.development` 文件:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

   如需生产环境配置，创建 `.env.production`:
   ```
   VITE_API_BASE_URL=https://api.yoursite.com/api
   ```

## 运行应用

### 开发环境

```bash
# 使用npm
npm run dev

# 或者使用yarn
yarn dev
```

应用将在 http://localhost:5174/ 运行

### 构建生产版本

```bash
# 使用npm
npm run build

# 或者使用yarn
yarn build
```

构建后的文件位于 `dist` 目录，可部署到任何静态文件服务器。

## 项目结构

```
frontend/
├── public/                # 静态资源目录
├── src/
│   ├── api/               # API请求模块
│   │   ├── index.js       # Axios实例配置
│   │   ├── auth.js        # 认证相关API
│   │   ├── books.js       # 图书管理API
│   │   ├── procurement.js # 采购管理API
│   │   ├── sales.js       # 销售管理API
│   │   ├── finance.js     # 财务管理API
│   │   └── users.js       # 用户管理API
│   ├── assets/            # 图片、字体等资源
│   ├── components/        # 可复用的组件
│   │   ├── BookForm.vue   # 图书表单组件
│   │   ├── BookTable.vue  # 图书列表表格
│   │   ├── OrderForm.vue  # 采购订单表单
│   │   ├── SaleForm.vue   # 销售表单
│   │   └── ...
│   ├── router/            # 路由配置
│   │   └── index.js
│   ├── store/             # Pinia状态管理
│   │   ├── auth.js        # 认证状态
│   │   ├── book.js        # 图书状态
│   │   ├── finance.js     # 财务状态
│   │   ├── procurement.js # 采购状态
│   │   └── sales.js       # 销售状态
│   ├── views/             # 页面组件
│   │   ├── LoginView.vue
│   │   ├── DashboardView.vue
│   │   ├── BookInventoryView.vue
│   │   ├── ProcurementView.vue
│   │   ├── SalesView.vue
│   │   ├── FinanceReportView.vue
│   │   ├── UserManagementView.vue
│   │   └── ProfileView.vue
│   ├── App.vue            # 根组件
│   └── main.js            # 应用入口
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
├── package.json           # 项目依赖和脚本
└── vite.config.js         # Vite配置
```

## 主要模块说明

### 认证模块
- 用户登录、注销功能
- 令牌管理和自动刷新
- 路由权限控制

### 图书管理
- 图书CRUD操作
- 库存管理
- 搜索与过滤

### 采购管理
- 创建采购订单
- 订单状态流转(未支付->已支付->已入库)
- 支持退货操作

### 销售管理
- 创建销售记录
- 支持多种支付方式
- 退款处理

### 财务报表
- 收入/支出统计
- 按日期筛选
- 按交易类型筛选

### 用户管理
- 用户CRUD操作(仅超级管理员)
- 个人资料编辑

## 开发规范

- 组件使用PascalCase命名(如`BookForm.vue`)
- API请求集中在api目录
- 状态管理使用Pinia stores
- 使用Vue Router处理导航
- 权限控制通过路由守卫实现

## 常见问题

**Q: API连接失败怎么办?**  
A: 检查`.env.development`中的API地址配置，确保后端服务正在运行。

**Q: 如何添加新页面?**  
A: 在`views`目录创建新组件，然后在`router/index.js`中添加路由配置。

**Q: 权限不足怎么处理?**  
A: 检查当前登录用户角色，某些操作需要超级管理员权限。

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。