$StartupFolder = [System.Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder 'TuTienBot_AutoStart.lnk'

if (Test-Path $ShortcutPath) {
    Remove-Item $ShortcutPath -Force
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host " [OK] DA GO BO TU DONG KHOI DONG CUNG PC THANH CONG!" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host "- Bot se KHONG tu dong khoi dong khi bat may tinh nua." -ForegroundColor Yellow
} else {
    Write-Host "[!] May tinh chua tung cai dat tu khoi dong cho bot nay." -ForegroundColor Yellow
}
