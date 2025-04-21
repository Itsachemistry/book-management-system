@echo off
title Book Management System Launcher

echo Starting Backend Server...
cd c:\Users\Elio\Desktop\book-management-system\bookstore_system\backend

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