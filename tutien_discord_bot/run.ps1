# PowerShell Script để quản lý và khởi động Tu Tiên Discord Bot
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 1. Kiểm tra Python
try {
    $pyVer = python --version 2>&1
} catch {
    Write-Host "[LỖI] Chưa cài đặt Python hoặc chưa thêm vào PATH!" -ForegroundColor Red
    Read-Host "Nhấn Enter để thoát..."
    exit 1
}

# 2. Kiểm tra .env
if (-not (Test-Path "$PSScriptRoot\.env")) {
    if (Test-Path "$PSScriptRoot\.env.example") {
        Write-Host "[!] Đang tạo .env từ .env.example..." -ForegroundColor Yellow
        Copy-Item "$PSScriptRoot\.env.example" "$PSScriptRoot\.env"
        Write-Host "[👉] Vui lòng điền DISCORD_TOKEN vào file .env vừa tạo!" -ForegroundColor Magenta
        notepad "$PSScriptRoot\.env"
        Read-Host "Sau khi điền token xong, nhấn Enter để tiếp tục..."
    } else {
        Write-Host "[LỖI] Không tìm thấy file .env!" -ForegroundColor Red
        Read-Host "Nhấn Enter để thoát..."
        exit 1
    }
}

# 3. Kích hoạt virtualenv nếu có
if (Test-Path "$PSScriptRoot\venv\Scripts\Activate.ps1") {
    & "$PSScriptRoot\venv\Scripts\Activate.ps1"
} elseif (Test-Path "$PSScriptRoot\.venv\Scripts\Activate.ps1") {
    & "$PSScriptRoot\.venv\Scripts\Activate.ps1"
}

# 4. Kiểm tra thư viện
python -c "import discord, dotenv" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Đang cài đặt thư viện từ requirements.txt..." -ForegroundColor Yellow
    pip install -r "$PSScriptRoot\requirements.txt"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[LỖI] Cài đặt thư viện thất bại!" -ForegroundColor Red
        Read-Host "Nhấn Enter để thoát..."
        exit 1
    }
}

function Show-Menu {
    Clear-Host
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "       ⛩️  BẢNG ĐIỀU KHIỂN TU TIÊN DISCORD BOT  ⛩️" -ForegroundColor Yellow
    Write-Host "======================================================" -ForegroundColor Cyan
    
    $botPid = $null
    if (Test-Path "$PSScriptRoot\bot.pid") {
        $botPid = Get-Content "$PSScriptRoot\bot.pid" -ErrorAction SilentlyContinue
    }
    
    $isOnline = $false
    if ($botPid) {
        $proc = Get-Process -Id $botPid -ErrorAction SilentlyContinue
        if ($proc) { $isOnline = $true }
    }
    
    $startupLnk = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\TuTienBot_AutoStart.lnk"
    $hasAutoStart = Test-Path $startupLnk
    
    if ($isOnline) {
        Write-Host "  [ Trạng Thái Bot ]: " -NoNewline
        Write-Host "🟢 ONLINE (PID: $botPid)" -ForegroundColor Green
    } else {
        Write-Host "  [ Trạng Thái Bot ]: " -NoNewline
        Write-Host "🔴 OFFLINE" -ForegroundColor Red
    }
    
    Write-Host "  [ Tự Động Theo PC]: " -NoNewline
    if ($hasAutoStart) {
        Write-Host "🔄 ĐÃ BẬT (Tự chạy khi mở PC)" -ForegroundColor Green
    } else {
        Write-Host "⚪ CHƯA BẬT" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "  [1] Chạy trực tiếp (Có cửa sổ xem log)" -ForegroundColor White
    Write-Host "  [2] Khởi động CHẠY NGẦM (Ẩn cửa sổ - Chạy trong nền)" -ForegroundColor Green
    Write-Host "  [3] Dừng bot (Tắt bot đang chạy ngầm)" -ForegroundColor Red
    Write-Host "  [4] Kiểm tra trạng thái chi tiết & Xem Log" -ForegroundColor Yellow
    Write-Host "  [5] BẬT tự động Mở/Tắt theo máy tính (Auto-Start)" -ForegroundColor Cyan
    Write-Host "  [6] TẮT tự động Mở/Tắt theo máy tính" -ForegroundColor Magenta
    Write-Host "  [0] Thoát" -ForegroundColor DarkGray
    Write-Host "======================================================" -ForegroundColor Cyan
    
    $choice = Read-Host "Nhập lựa chọn của bạn [1 - 6, 0]"
    switch ($choice) {
        "1" {
            Clear-Host
            Write-Host "[*] Đang khởi động bot..." -ForegroundColor Green
            Write-Host "------------------------------------------------------" -ForegroundColor DarkGray
            python "$PSScriptRoot\main.py"
            Write-Host ""
            Write-Host "Bot đã dừng hoạt động." -ForegroundColor Yellow
            Read-Host "Nhấn Enter để tiếp tục..."
            Show-Menu
        }
        "2" {
            & "$PSScriptRoot\start_chay_ngam.bat"
            Show-Menu
        }
        "3" {
            & "$PSScriptRoot\stop_chay_ngam.bat"
            Show-Menu
        }
        "4" {
            & "$PSScriptRoot\check_trang_thai.bat"
            Show-Menu
        }
        "5" {
            & "$PSScriptRoot\cai_dat_khoi_dong_cung_windows.bat"
            Show-Menu
        }
        "6" {
            & "$PSScriptRoot\go_khoi_dong_cung_windows.bat"
            Show-Menu
        }
        "0" {
            exit 0
        }
        default {
            Show-Menu
        }
    }
}

Show-Menu
