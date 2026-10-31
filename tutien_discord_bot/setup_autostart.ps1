$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = [System.Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder 'TuTienBot_AutoStart.lnk'
$TargetScript = Join-Path $PSScriptRoot 'start_chay_ngam.vbs'

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = 'wscript.exe'
$Shortcut.Arguments = ('"' + $TargetScript + '"')
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = 'Tu dong chay ngam Tu Tien Discord Bot khi bat may tinh'
$Shortcut.Save()

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " [OK] DA THIET LAP TU DONG KHOI DONG CUNG PC THANH CONG!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ("- Shortcut: " + $ShortcutPath) -ForegroundColor Gray
Write-Host ("- File chay: " + $TargetScript) -ForegroundColor Gray
Write-Host ""
Write-Host "Tu nay khi BAT may tinh, bot se TU DONG chay ngam trong nen Windows." -ForegroundColor Yellow
Write-Host "Khi TAT may tinh, bot se TU DONG tat theo he dieu hanh." -ForegroundColor Yellow
