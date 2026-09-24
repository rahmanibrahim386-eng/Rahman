$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$startup = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
$launcher = Join-Path $startup 'M268 Dashboard Online.cmd'
$content = "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$root\start_m268_online.ps1`""
Set-Content -Path $launcher -Value $content -Encoding UTF8
Write-Host "Startup launcher created: $launcher"
