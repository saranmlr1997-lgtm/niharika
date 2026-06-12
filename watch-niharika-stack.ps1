$ErrorActionPreference = "Continue"

$ScriptPath = "C:\Users\saran\niharika\start-niharika-stack.ps1"
$LogPath = "C:\Users\saran\niharika\niharika-watchdog.log"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        $result = powershell.exe -ExecutionPolicy Bypass -File $ScriptPath
        Add-Content -Path $LogPath -Value "$timestamp $result"
    } catch {
        Add-Content -Path $LogPath -Value "$timestamp ERROR $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 300
}
