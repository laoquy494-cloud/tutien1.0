@echo off
title Dung Bot Chay Ngam - Tu Tien Discord Bot
cls
echo =======================================================
echo          DUNG TU TIEN DISCORD BOT CHAY NGAM
echo =======================================================
echo.

if exist "%~dp0bot.pid" (
    for /f "usebackq delims=" %%i in ("%~dp0bot.pid") do (
        echo [*] Dang dung tien trinh Bot PID: %%i...
        taskkill /F /PID %%i >nul 2>&1
    )
    del /f /q "%~dp0bot.pid" >nul 2>&1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { (.Name -like 'python*') -and (.CommandLine -like '*tutien_discord_bot*') } | ForEach-Object { Stop-Process -Id .ProcessId -Force -ErrorAction SilentlyContinue; Write-Host ('[*] Da dung tien trinh PID: ' + .ProcessId) }" >nul 2>&1

echo.
echo =======================================================
echo  [OK] DA DUNG BOT TU TIEN THANH CONG!
echo =======================================================
echo.
pause