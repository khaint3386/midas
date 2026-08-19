@echo off
chcp 65001 >nul
title Midas - Quet VN30
cd /d %~dp0
if not exist .venv ( echo Chua cai dat - chay start_midas.bat truoc. & pause & exit /b 1 )
.venv\Scripts\python scan_batch.py 60 VN30
pause
