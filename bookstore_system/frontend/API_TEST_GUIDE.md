# API测试指南

## 解决CORS问题

当从`file://`协议下打开HTML文件时，由于浏览器安全限制，无法向HTTP服务器发送请求。这是一个CORS (跨源资源共享) 限制。

## 如何正确测试API连接

请按照以下三种方法之一来访问测试页面：

### 方法1：使用提供的批处理文件（最简单）

1. 确保Node.js已安装
2. 双击运行项目中的`start-test-server.bat`文件
3. 在浏览器中访问 http://localhost:3000

### 方法2：手动运行Node.js服务器

1. 打开命令提示符或终端
2. 导航到前端目录：`cd path\to\bookstore_system\frontend`
3. 运行：`node serve-test.js`
4. 在浏览器中访问 http://localhost:3000

### 方法3：通过Vite开发服务器访问

如果您已经在运行Vite开发服务器：

1. 运行：`npm run dev`
2. 在浏览器中访问 http://localhost:5174/standalone-test.html

## 测试项目内容

测试页面包含三部分测试：

1. **服务可用性检查**：验证后端服务器是否在运行
2. **基础连接测试**：测试API的基本连接
3. **登录测试**：尝试使用提供的凭据进行登录

## 常见问题排查

如果仍然遇到CORS错误，请检查：

1. 后端服务器是否已启动 (`flask run`)
2. 后端服务器的CORS配置是否包含您的前端URL
3. 浏览器控制台中是否有其他错误信息
