@echo off
title Khoi Dong Bot Chay Ngam - Tu Tien Discord Bot
cls
echo =======================================================
echo          TU TIEN DISCORD BOT - KHOI DONG CHAY NGAM
echo =======================================================
echo.

set IS_RUNNING=0
if exist "%~dp0bot.pid" (
    for /f "usebackq delims=" %%i in ("%~dp0bot.pid") do (
        tasklist /FI "PID eq %%i" 2>nul | findstr /I "python" >nul
        if not errorlevel 1 (
            set IS_RUNNING=1
            set RUN_PID=%%i
        )
    )
)

if "%IS_RUNNING%"=="1" goto :already_running

echo [*] Dang khoi dong bot chay ngam trong nen Windows...
wscript.exe "%~dp0start_chay_ngam.vbs"

ping 127.0.0.1 -n 4 >nul

set SUCCESS=0
if exist "%~dp0bot.pid" (
    for /f "usebackq delims=" %%i in ("%~dp0bot.pid") do (
        tasklist /FI "PID eq %%i" 2>nul | findstr /I "python" >nul
        if not errorlevel 1 (
            set SUCCESS=1
            set RUN_PID=%%i
        )
    )
)

if "%SUCCESS%"=="1" goto :started_ok

echo.
echo [!] Bot dang khoi dong... Hay kiem tra log tai file 'bot.log' hoac chay 'check_trang_thai.bat'.
pause
exit /b 0

:already_running
echo [!] Bot hien DANG CHAY NGAM roi - PID: %RUN_PID%
echo     Neu muon khoi dong lai, vui long chay 'stop_chay_ngam.bat' truoc.
echo.
echo =======================================================
pause
exit /b 0

:started_ok
echo.
echo =======================================================
echo  OK: BOT DA DUOC KHOI DONG CHAY NGAM THANH CONG!
echo =======================================================
echo.
echo  - PID tien trinh: %RUN_PID%
echo  - Trang thai:     Dang chay an trong nen Windows 24/7.
echo  - Ban co the DONG CUA SO NAY ma bot van hoat dong binh thuong!
echo.
echo  * Kiem tra trang thai: chay file 'check_trang_thai.bat'
echo  * Tat bot chay ngam:   chay file 'stop_chay_ngam.bat'
echo  * Tu dong mo theo PC:  chay file 'cai_dat_khoi_dong_cung_windows.bat'
echo.
echo =======================================================
pause
exit /b 0