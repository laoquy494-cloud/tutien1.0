@echo off
title Kiem Tra Trang Thai - Tu Tien Discord Bot

:refresh
cls
echo =======================================================
echo        KIEM TRA TRANG THAI TU TIEN DISCORD BOT
echo =======================================================
echo.

set BOTPID=
if exist "%~dp0bot.pid" (
    for /f "usebackq delims=" %%i in ("%~dp0bot.pid") do set BOTPID=%%i
)

if defined BOTPID (
    tasklist /FI "PID eq %BOTPID%" 2>nul | findstr /I "python" >nul
    if not errorlevel 1 (
        echo  [TRANG THAI]:        ONLINE - Dang hoat dong 24/7
        echo  [PID TIEN TRINH]:    %BOTPID%
        powershell -NoProfile -Command "try { $p = Get-Process -Id %BOTPID% -ErrorAction Stop; $ram = [math]::Round($p.WorkingSet64 / 1MB, 1); $st = $p.StartTime.ToString('yyyy-MM-dd HH:mm:ss'); Write-Host ('  [BO NHO RAM]:        ' + $ram + ' MB'); Write-Host ('  [KHOI CHAY LUC]:     ' + $st); } catch {}"
    ) else (
        echo  [TRANG THAI]:        OFFLINE - Da dung
    )
) else (
    echo  [TRANG THAI]:        OFFLINE - Da dung
)

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\TuTienBot_AutoStart.lnk" (
    echo  [TU DONG THEO PC]:   DA BAT - Tu mo khi bat PC, tat khi tat PC
) else (
    echo  [TU DONG THEO PC]:   CHUA BAT - Chay 'cai_dat_khoi_dong_cung_windows.bat' de bat
)

echo.
echo =======================================================
echo  15 DONG NHAT KY (LOG) MOI NHAT:
echo =======================================================
powershell -NoProfile -Command "if (Test-Path '%~dp0bot.log') { Get-Content '%~dp0bot.log' -Tail 15 -Encoding UTF8 } else { Write-Host '  (Chua co du lieu trong file bot.log)' }"
echo.
echo =======================================================
echo  [1] Khoi dong chay ngam   [2] Dung bot   [3] Lam moi   [0] Thoat
echo =======================================================
choice /C 1230 /N /M "Nhap lua chon cua ban [1, 2, 3, 0]: "
if errorlevel 4 exit /b 0
if errorlevel 3 goto :refresh
if errorlevel 2 (
    call "%~dp0stop_chay_ngam.bat"
    goto :refresh
)
if errorlevel 1 (
    call "%~dp0start_chay_ngam.bat"
    goto :refresh
)