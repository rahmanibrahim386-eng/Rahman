$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
$port = 8000

if (-not (Test-Path $python)) {
    $python = 'python.exe'
}

$listeners = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
if ($listeners.Count -gt 0) {
    $processIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($processId in $processIds) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $process.Id
        }
    }
    Write-Host "M268 dashboard server stopped."
} else {
    $env:DASHBOARD_PASSWORD = 'rahman'
    Start-Process -FilePath $python `
        -ArgumentList "`"$root\dashboard_server.py`" $port" `
        -WorkingDirectory $root `
        -WindowStyle Minimized
    Write-Host "M268 dashboard server started at http://localhost:$port/Mr.RI"
}

Start-Sleep -Seconds 1
Read-Host 'Press Enter to close'
