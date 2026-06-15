$ErrorActionPreference = "Stop"

$ProjectDir = "C:\Users\saran\niharika"
$PythonExe = "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$CloudflaredExe = Join-Path $ProjectDir "cloudflared.exe"
$CloudflaredConfig = "C:\Users\saran\.cloudflared\config.yml"
$SecretsPath = Join-Path $ProjectDir "niharika-secrets.ps1"

if (Test-Path $SecretsPath) {
    . $SecretsPath
}

function Test-CommandLineProcess {
    param([string]$Needle)
    $processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue
    return [bool]($processes | Where-Object { $_.CommandLine -like "*$Needle*" })
}

function Start-NiharikaApp {
    if (Test-CommandLineProcess "app.py") {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -like "*app.py*" } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    }
    if (-not (Test-CommandLineProcess "flask_app.py")) {
        $env:HOST = "0.0.0.0"
        $env:PORT = "8080"
        Start-Process -FilePath $PythonExe -ArgumentList "flask_app.py" -WorkingDirectory $ProjectDir -WindowStyle Hidden
    }
}

function Start-NinaApp {
    if (-not (Test-CommandLineProcess "nina.py")) {
        $env:NINA_PORT = "5000"
        Start-Process -FilePath $PythonExe -ArgumentList "nina.py" -WorkingDirectory $ProjectDir -WindowStyle Hidden
    }
}

function Start-NiharikaTunnel {
    if (-not (Test-CommandLineProcess "niharika-wholesale")) {
        Start-Process -FilePath $CloudflaredExe -ArgumentList "tunnel --config `"$CloudflaredConfig`" --logfile cloudflared-named-niharika.log --protocol http2 run niharika-wholesale" -WorkingDirectory $ProjectDir -WindowStyle Hidden
    }
}

Start-NiharikaApp
Start-NinaApp
Start-NiharikaTunnel

Start-Sleep -Seconds 3

$status = [ordered]@{
    niharika_local = $false
    nina_local = $false
    tunnel = Test-CommandLineProcess "niharika-wholesale"
}

try {
    $status.niharika_local = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8080/" -TimeoutSec 5).StatusCode -eq 200
} catch {}

try {
    $status.nina_local = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:5000/" -TimeoutSec 5).StatusCode -eq 200
} catch {}

$status | ConvertTo-Json
