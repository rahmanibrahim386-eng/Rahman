$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
$cloudflared = Join-Path $env:USERPROFILE 'cloudflared\cloudflared.exe'
$log = Join-Path $root 'cloudflared.log'
$errorLog = Join-Path $root 'cloudflared-error.log'

if (-not (Test-Path $python)) { $python = 'python.exe' }
if (-not (Test-Path $cloudflared)) {
    $cloudflared = (Get-Command cloudflared.exe -ErrorAction SilentlyContinue).Source
}
if (-not $cloudflared) { throw 'cloudflared.exe tidak ditemukan.' }

$server = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $server) {
    $env:DASHBOARD_PASSWORD = 'rahman'
    Start-Process -FilePath $python -ArgumentList "`"$root\dashboard_server.py`" 8000" -WorkingDirectory $root -WindowStyle Hidden
}

$tunnel = Get-CimInstance Win32_Process -Filter "Name = 'cloudflared.exe'" |
    Where-Object { $_.CommandLine -like '*tunnel*--url*localhost:8000*' }
if (-not $tunnel) {
    Start-Process -FilePath $cloudflared `
        -ArgumentList 'tunnel --url http://localhost:8000' `
        -WorkingDirectory $root `
        -RedirectStandardOutput $log `
        -RedirectStandardError $errorLog `
        -WindowStyle Hidden
}
