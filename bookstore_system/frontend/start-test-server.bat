@echo off
echo 启动API测试服务器...
cd "%~dp0"
npm install http-proxy
node serve-test.js
