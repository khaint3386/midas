@echo off
chcp 65001 >nul
cd /d %~dp0
if not exist .venv (
  echo Chua cai dat - hay chay start_midas.bat truoc.
  pause & exit /b 1
)
.venv\Scripts\python scan_batch.py %1
pause
