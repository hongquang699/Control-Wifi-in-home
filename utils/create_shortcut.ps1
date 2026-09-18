$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop 'Network Manager.lnk'

$projectDir = Split-Path -Parent $PSScriptRoot
$exePath = Join-Path $projectDir 'dist\NetworkManager\NetworkManager.exe'

if (-not (Test-Path $exePath)) {
    $exePath = Join-Path $projectDir 'run.bat'
}

$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $projectDir
$shortcut.Description = 'Network Manager - Quản lý và Giám sát Mạng Nội bộ'
$shortcut.Save()

Write-Host "Đã tạo lối tắt thành công tại: $shortcutPath"
