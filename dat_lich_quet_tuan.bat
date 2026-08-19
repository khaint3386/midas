@echo off
chcp 65001 >nul
title Midas - Dat lich loc tuan TOP 12
:: Dang ky Windows Task Scheduler: loc tuan VN100 -> TOP 12 watchlist
:: 8h sang thu 7 hang tuan (thi truong dong cua - du lieu tuan da day du)
schtasks /Create /F /SC WEEKLY /D SAT /ST 08:00 /TN "Midas_Loc_Tuan_Top12" /TR "\"%~dp0loc_tuan.bat\""
if errorlevel 1 (
  echo.
  echo [LOI] Can chay file nay bang QUYEN ADMIN: chuot phai - Run as administrator
) else (
  echo.
  echo [OK] Da dat lich: loc tuan VN100 chon TOP 12 luc 08:00 sang thu 7 hang tuan.
  echo Watchlist duoc thay hoan toan bang 12 ma diem cao nhat (60%% 4M + 40%% VCP).
  echo Bao cao luu vao: %~dp0data\bao_cao_loc_tuan_*.md
  echo Xem/xoa lich: schtasks /Query /TN Midas_Loc_Tuan_Top12  hoac  /Delete
)
pause
