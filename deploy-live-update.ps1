$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LiveDir = "C:\Users\saran\niharika"
$RestartScript = Join-Path $LiveDir "start-niharika-stack.ps1"

$excludeNames = @(
    ".git",
    ".gitignore",
    "niharika-secrets.ps1",
    "server.out.log",
    "server.err.log",
    "nina.out.log",
    "nina.err.log",
    "cloudflared-named-niharika.log",
    "niharika-watchdog.log",
    "__pycache__"
)

if (-not (Test-Path $LiveDir)) {
    throw "Live directory not found: $LiveDir"
}

Get-ChildItem -LiteralPath $RepoDir -Force | Where-Object {
    $excludeNames -notcontains $_.Name
} | ForEach-Object {
    $source = $_.FullName
    $target = Join-Path $LiveDir $_.Name

    if ($_.PSIsContainer) {
        robocopy $source $target /MIR /XD __pycache__ .git | Out-Null
        if ($LASTEXITCODE -gt 7) {
            throw "robocopy failed for $source with exit code $LASTEXITCODE"
        }
    } else {
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
}

if (-not (Test-Path $RestartScript)) {
    throw "Restart script not found: $RestartScript"
}

powershell -ExecutionPolicy Bypass -File $RestartScript
