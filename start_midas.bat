@echo off
chcp 65001 >nul
title MIDAS 3.0
cd /d %~dp0
echo ============================================
echo   MIDAS 3.0 - Cham vao dau, vang o do
echo ============================================
echo.

:: [1/5] Kiem tra Python
where python >nul 2>&1
if errorlevel 1 (
  echo [LOI] Chua cai Python. Tai tai: https://www.python.org/downloads/
  echo Khi cai nho tick "Add Python to PATH".
  pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [1/5] Python %%v - OK

:: [2/5] Tao moi truong ao + cai thu vien (chi lan dau)
if not exist .venv (
  echo [2/5] Lan dau chay: tao moi truong ao va cai thu vien...
  echo       (mat 2-5 phut, chi can 1 lan)
  python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip -q
  .venv\Scripts\pip install -r requirements.txt
  if errorlevel 1 (
    echo [LOI] Cai thu vien that bai. Kiem tra ket noi internet roi chay lai.
    pause & exit /b 1
  )
) else (
  echo [2/5] Moi truong ao da co - OK
)

:: [3/5] Tao file .env neu chua co
if not exist .env (
  copy .env.example .env >nul
  echo [3/5] Da tao .env - Mo file .env de dien GEMINI_API_KEY khi co key moi
) else (
  echo [3/5] File .env da co - OK
)

:: [4/5] Giai phong cong 8386 neu phien Midas cu con chay ngam
::       (tranh loi [Errno 10048] va trinh duyet noi chuyen voi code cu)
set FOUND_OLD=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r ":8386 .*LISTENING"') do (
  set FOUND_OLD=1
  taskkill /F /PID %%p >nul 2>&1
)
if "%FOUND_OLD%"=="1" (
  echo [4/5] Da tat phien Midas cu dang chiem cong 8386 - OK
  timeout /t 2 /nobreak >nul
) else (
  echo [4/5] Cong 8386 trong - OK
)

:: [5/5] Khoi dong server + mo trinh duyet
echo [5/5] Khoi dong Midas tai http://127.0.0.1:8386 ...
start "" http://127.0.0.1:8386
.venv\Scripts\python run.py
pause
