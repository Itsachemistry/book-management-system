const http = require('http');
const fs = require('fs');
const path = require('path');
const httpProxy = require('http-proxy');

const PORT = 3000;
const API_URL = 'http://127.0.0.1:5000';

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
};

// 创建代理
const proxy = httpProxy.createProxyServer({
  target: API_URL,
  changeOrigin: true
});

// 处理代理错误
proxy.on('error', (err, req, res) => {
  console.error('代理错误:', err);
  res.writeHead(500, {'Content-Type': 'text/plain'});
  res.end('代理请求失败: ' + err.message);
});

const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // API代理
  if (req.url.startsWith('/api')) {
    return proxy.web(req, res, { target: API_URL });
  }

  // 专门处理根路径，尝试提供index.html
  if (req.url === '/') {
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    if (fs.existsSync(indexPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      fs.createReadStream(indexPath).pipe(res);
      return;
    }
    
    // 如果dist中不存在，尝试提供public/index.html
    const publicIndexPath = path.join(__dirname, 'public', 'index.html');
    if (fs.existsSync(publicIndexPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      fs.createReadStream(publicIndexPath).pipe(res);
      return;
    }
    
    // 如果都不存在，提供测试页面
    const testPath = path.join(__dirname, 'public', 'standalone-test.html'); 
    if (fs.existsSync(testPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      fs.createReadStream(testPath).pipe(res);
      return;
    }
  }
  
  // favicon处理 
  if (req.url === '/favicon.ico') {
    const faviconPath = path.join(__dirname, 'public', 'favicon.ico');
    if (fs.existsSync(faviconPath)) {
      res.writeHead(200, { 'Content-Type': 'image/x-icon' });
      fs.createReadStream(faviconPath).pipe(res);
      return;
    } else {
      // 使用空的favicon响应
      res.writeHead(200, { 'Content-Type': 'image/x-icon' });
      res.end();
      return;
    }
  }
  
  // 默认提供standalone-test.html
  let filePath = req.url === '/' ? 
    path.join(__dirname, 'public', 'standalone-test.html') : 
    path.join(__dirname, req.url);
  
  // 设置 CORS 头，允许本地开发环境的请求
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // 对于 OPTIONS 请求（预检请求）返回适当的 CORS 头
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.writeHead(204); // 204 No Content
    res.end();
    return;
  }
  
  // 检测文件扩展名
  const extname = path.extname(filePath);
  let contentType = MIME_TYPES[extname] || 'text/plain';
  
  // 读取文件
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // 尝试在public目录中查找
        const publicPath = path.join(__dirname, 'public', req.url);
        fs.readFile(publicPath, (err2, content2) => {
          if (err2) {
            res.writeHead(404);
            res.end('文件不存在');
          } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content2);
          }
        });
      } else {
        res.writeHead(500);
        res.end(`服务器错误: ${err.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
});

server.listen(PORT, () => {
  console.log(`测试服务器运行在 http://localhost:${PORT}`);
  console.log(`访问 http://localhost:${PORT} 打开测试页面`);
  console.log(`API请求将代理到 ${API_URL}/api`);
});
