$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$HomeUrl = "http://127.0.0.1:8080/"
$DashboardUrl = "http://127.0.0.1:8080/business"

function Test-CommandLineProcess {
    param([string]$Needle)
    $processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue
    return [bool]($processes | Where-Object { $_.CommandLine -like "*$Needle*" })
}

function Start-LocalApp {
    if (-not (Test-Path $PythonExe)) {
        throw "Python runtime not found at $PythonExe"
    }

    if (-not (Test-CommandLineProcess "flask_app.py")) {
        $env:HOST = "127.0.0.1"
        $env:PORT = "8080"
        Start-Process -FilePath $PythonExe -ArgumentList "flask_app.py" -WorkingDirectory $ProjectDir -WindowStyle Hidden
    }

    if (-not (Test-CommandLineProcess "nina.py")) {
        $env:NINA_PORT = "5000"
        Start-Process -FilePath $PythonExe -ArgumentList "nina.py" -WorkingDirectory $ProjectDir -WindowStyle Hidden
    }
}

function Wait-ForSite {
    param([string]$Url)
    for ($i = 0; $i -lt 25; $i++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                return
            }
        } catch {}
        Start-Sleep -Milliseconds 800
    }
    throw "Niharika app did not start in time."
}

function Get-EdgePath {
    $candidates = @(
        "$Env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe",
        "$Env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }
    $command = Get-Command msedge.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    return $null
}

Start-LocalApp
Wait-ForSite -Url $HomeUrl

$EdgePath = Get-EdgePath
if ($EdgePath) {
    Start-Process -FilePath $EdgePath -ArgumentList "--app=$DashboardUrl"
} else {
    Start-Process $DashboardUrl
}

Write-Output "Niharika desktop app launched."
