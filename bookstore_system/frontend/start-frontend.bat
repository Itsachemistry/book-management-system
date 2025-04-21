@echo off
cd "%~dp0"
echo 正在安装http-proxy（用于测试服务器）...
call npm install http-proxy --no-save

echo.
echo 启动选项:
echo 1. 启动Vue开发服务器 (npm run dev)
echo 2. 启动测试服务器 (node serve-test.js)
echo 3. 同时启动两个服务器
echo.

set /p choice=请选择 (1-3): 

if "%choice%"=="1" (
    echo 正在启动Vue开发服务器...
    start cmd /k "npm run dev"
) else if "%choice%"=="2" (
    echo 正在启动测试服务器...
    start cmd /k "node serve-test.js"
) else if "%choice%"=="3" (
    echo 同时启动两个服务器...
    start cmd /k "npm run dev"
    timeout /t 3 /nobreak > nul
    start cmd /k "node serve-test.js"
) else (
    echo 无效选择！
)

echo.
echo 提示: Vue开发服务器运行在 http://localhost:5174
echo 提示: 测试服务器运行在 http://localhost:3000
echo.
pause
