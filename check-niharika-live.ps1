$ErrorActionPreference = "Continue"

$checks = [ordered]@{}

try {
    $checks["localhost_niharika"] = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8080/" -TimeoutSec 8).StatusCode
} catch {
    $checks["localhost_niharika"] = "down"
}

try {
    $checks["localhost_admin"] = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8080/admin" -TimeoutSec 8).StatusCode
} catch {
    $checks["localhost_admin"] = "down"
}

try {
    $checks["localhost_nina"] = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:5000/" -TimeoutSec 8).StatusCode
} catch {
    $checks["localhost_nina"] = "down"
}

try {
    $checks["www_niharika_dns"] = (Resolve-DnsName "www.niharika.com" -ErrorAction Stop | Select-Object -First 3 | ForEach-Object { "$($_.Type):$($_.IPAddress)$($_.NameHost)" }) -join ", "
} catch {
    $checks["www_niharika_dns"] = "not resolving"
}

try {
    $checks["nina_niharika_dns"] = (Resolve-DnsName "nina.niharika.com" -ErrorAction Stop | Select-Object -First 3 | ForEach-Object { "$($_.Type):$($_.IPAddress)$($_.NameHost)" }) -join ", "
} catch {
    $checks["nina_niharika_dns"] = "not resolving"
}

$checks | ConvertTo-Json
