@echo off
chcp 65001 > nul
cd "%~dp0"
echo 正在安装http-proxy（用于测试服务器）...
call npm install http-proxy --no-save

echo.
echo ==== 局域网访问信息 ====
powershell -Command "try { Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notmatch '127.0.0.1' -and $_.IPAddress -notmatch '169.254.*'} | ForEach-Object { Write-Host ('Vue服务: http://' + $_.IPAddress + ':5174'); Write-Host ('测试服务: http://' + $_.IPAddress + ':3000'); Write-Host ('接口:' + $_.InterfaceAlias) } } catch { Write-Host '无法获取网络信息，但您可以尝试使用Vite显示的Network地址' }"
echo =====================
echo 提示: 看到"Network:"字样的地址可以分享给同一网络的室友访问
echo 移动设备(iPad/手机)访问方法:
echo 1. 确保移动设备与电脑连接到同一WiFi网络
echo 2. 在iPad/手机浏览器中输入以"WLAN"接口开头的地址(通常是http://192.168.1.XXX:5174)
echo =====================
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
echo 室友可以通过局域网IP地址访问（见上方显示的地址）
echo.
pause
