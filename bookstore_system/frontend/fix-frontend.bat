@echo off
cd "%~dp0"
echo ===================================================
echo           前端应用修复工具
echo ===================================================
echo.
echo 正在执行修复步骤...

echo 1. 清理缓存...
rmdir /s /q node_modules\.vite 2>nul
del /f /q node_modules\.cache 2>nul

echo 2. 安装依赖...
call npm install --silent

echo 3. 启动开发服务器(使用--force强制重新构建)
echo.
echo 服务器启动后，请访问: http://localhost:5174
echo 如果浏览器没有自动打开，请手动访问上述地址
echo.
echo 按Ctrl+C可停止服务器
echo.
npm run dev -- --force

pause
