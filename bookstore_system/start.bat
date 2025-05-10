@echo off
title Book Management System Launcher
chcp 65001 > nul

echo Starting Backend Server...
cd c:\Users\Elio\Desktop\book-management-system\bookstore_system\backend

:: 显示局域网IP地址，方便分享给室友
echo.
echo ==== 网络信息（分享给室友使用）====
powershell -Command "try { Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notmatch '127.0.0.1' -and $_.IPAddress -notmatch '169.254.*'} | ForEach-Object { Write-Host ('局域网IP: ' + $_.IPAddress + ' (接口: ' + $_.InterfaceAlias + ')') } } catch { Write-Host '无法获取网络信息，但您可以尝试使用前端服务显示的Network地址' }"
echo ============================
echo 提示: 前端启动后，可以看到"Network:"字样的地址，可以分享给同一网络的室友访问
echo 移动设备(如iPad/手机)访问指南:
echo 1. 确保移动设备与电脑连接到同一WiFi
echo 2. 在移动设备浏览器中输入"Network:"后显示的地址(通常是http://192.168.1.XXX:5174)
echo 3. 建议使用WLAN接口(WiFi)的地址，如显示中的192.168.1.103:5174
echo ============================
echo.

:: Start backend in a new command prompt window
:: Set Execution Policy for the process, activate venv, and run Flask
start "Backend" cmd /k "powershell -Command Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force & venv\Scripts\activate & flask run"

echo Waiting for backend to initialize (optional delay)...
timeout /t 5 /nobreak > nul

echo Starting Frontend Development Server...
cd c:\Users\Elio\Desktop\book-management-system\bookstore_system\frontend

:: Start frontend in the current window
npm run dev

echo Both servers should be running. Backend is in a separate window.
pause