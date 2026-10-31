@echo off
title Tu Tien Discord Bot - Bang Dieu Khien

:: 1. Kiem tra Python da cai dat chua
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ======================================================
    echo [LOI] May tinh chua cai dat Python hoac chua them Python vao PATH!
    echo Vui long tai va cai dat Python tu: https://www.python.org/
    echo Nho tich chon "Add Python to PATH" khi cai dat.
    echo ======================================================
    pause
    exit /b 1
)

:: 2. Kiem tra file .env
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        echo [CANH BAO] Chua tim thay file .env, dang tu dong tao tu .env.example...
        copy "%~dp0.env.example" "%~dp0.env" > nul
        echo Da tao file .env thanh cong!
        echo.
        echo [!] Vui long mo file .env va dien DISCORD_TOKEN truoc khi chay bot!
        echo.
        notepad "%~dp0.env"
        pause
        exit /b 1
    ) else (
        echo [LOI] Khong tim thay file .env va .env.example!
        pause
        exit /b 1
    )
)

:: 3. Kich hoat moi truong ao (neu co)
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
) else if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

:: 4. Kiem tra thu vien can thiet
python -c "import discord, dotenv" > nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Dang tu dong cai dat thu vien tu requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [LOI] Cai dat thu vien that bai! Vui long kiem tra lai ket noi mang.
        pause
        exit /b 1
    )
    echo [*] Cai dat thu vien thanh cong!
    echo.
)

:menu
cls
echo ======================================================
echo       BANG DIEU KHIEN TU TIEN DISCORD BOT
echo ======================================================
echo.

set CURRENT_STATUS=OFFLINE
set CURRENT_PID=
if exist "%~dp0bot.pid" (
    for /f "usebackq delims=" %%i in ("%~dp0bot.pid") do (
        tasklist /FI "PID eq %%i" 2>nul | findstr /I "python" >nul
        if not errorlevel 1 (
            set CURRENT_STATUS=ONLINE - PID: %%i
            set CURRENT_PID=%%i
        )
    )
)

set AUTOSTART_STATUS=Chua bat
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\TuTienBot_AutoStart.lnk" (
    set AUTOSTART_STATUS=DA BAT - Tu mo khi bat PC
)

echo   [ Trang Thai Bot ]: %CURRENT_STATUS%
echo   [ Tu Dong Theo PC]: %AUTOSTART_STATUS%
echo.
echo ======================================================
echo   [1] Chay truc tiep (Co cua so CMD xem log)
echo   [2] Khoi dong CHAY NGAM (An cua so - Chay trong nen 24/7)
echo   [3] Dung bot (Tat bot dang chay ngam)
echo   [4] Kiem tra trang thai chi tiet va Xem Log
echo   [5] BAT tu dong Mo/Tat theo may tinh (Auto-Start PC)
echo   [6] TAT tu dong Mo/Tat theo may tinh
echo   [0] Thoat
echo ======================================================
choice /C 1234560 /N /M "Nhap lua chon cua ban [1 - 6, 0]: "

if errorlevel 7 exit /b 0
if errorlevel 6 goto :opt_disable_auto
if errorlevel 5 goto :opt_enable_auto
if errorlevel 4 goto :opt_check
if errorlevel 3 goto :opt_stop
if errorlevel 2 goto :opt_start_bg
if errorlevel 1 goto :opt_run_direct

:opt_run_direct
cls
echo ======================================================
echo   KHOI CHAY BOT TRUC TIEP (CONSOLE MODE)
echo ======================================================
echo [*] Dang khoi dong bot tu tien...
echo ------------------------------------------------------
python main.py
echo.
echo ------------------------------------------------------
echo Bot da dung hoat dong.
pause
goto :menu

:opt_start_bg
call "%~dp0start_chay_ngam.bat"
goto :menu

:opt_stop
call "%~dp0stop_chay_ngam.bat"
goto :menu

:opt_check
call "%~dp0check_trang_thai.bat"
goto :menu

:opt_enable_auto
call "%~dp0cai_dat_khoi_dong_cung_windows.bat"
goto :menu

:opt_disable_auto
call "%~dp0go_khoi_dong_cung_windows.bat"
goto :menu