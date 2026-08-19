@echo off
chcp 65001 >nul
title Midas - Loc tuan TOP 12 (VN100)
cd /d "%~dp0"
.venv\Scripts\python loc_tuan.py VN100
pause
