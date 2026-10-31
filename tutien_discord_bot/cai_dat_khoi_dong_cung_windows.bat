@echo off
title Cai Dat Tu Mo/Tat Theo PC - Tu Tien Discord Bot
cls
echo =======================================================
echo   CAI DAT BOT TU DONG MO VA TAT THEO MAY TINH (PC)
echo =======================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_autostart.ps1"

echo.
echo -------------------------------------------------------
set IS_RUNNING=0
if exist "%~dp0bot.pid" (
    for /f "usebackq delims=" %%i in ("%~dp0bot.pid") do (
        tasklist /FI "PID eq %%i" 2>nul | findstr /I "python" >nul
        if not errorlevel 1 set IS_RUNNING=1
    )
)

if "%IS_RUNNING%"=="0" (
    echo [?] Bot hien chua chay. Ban co muon khoi dong chay ngam ngay bay gio khong?
    set /p ASK_START="    Bam 'Y' de chay ngay, hoac phim bat ky de bo qua: "
    if /i "%ASK_START%"=="Y" (
        echo.
        echo [*] Dang khoi dong bot chay ngam...
        wscript.exe "%~dp0start_chay_ngam.vbs"
        timeout /t 2 >nul
        echo [OK] Da khoi dong! Ban co the kiem tra qua file 'check_trang_thai.bat'.
    )
) else (
    echo [OK] Bot hien dang chay ngam san sang!
)

echo.
echo =======================================================
echo  - De huy tu mo cung may tinh: chay 'go_khoi_dong_cung_windows.bat'
echo  - De kiem tra trang thai bot:  chay 'check_trang_thai.bat'
echo =======================================================
pause