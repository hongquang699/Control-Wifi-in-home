# Refresh Windows icon cache
Stop-Process -Name explorer -Force
Start-Sleep -Milliseconds 1200
$cachePath = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Explorer'
if (Test-Path $cachePath) {
    Get-ChildItem -Path $cachePath -Filter 'iconcache_*.db' -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
}
$mainCache = Join-Path $env:LOCALAPPDATA 'IconCache.db'
if (Test-Path $mainCache) {
    Remove-Item -Path $mainCache -Force -ErrorAction SilentlyContinue
}
Start-Process explorer
Write-Host 'Windows Explorer icon cache refreshed successfully.'