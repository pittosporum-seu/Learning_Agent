param(
    [string]$Lab = "01-strategy-intake",
    [int]$Port = 8765,
    [string]$HostName = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$server = Join-Path $root "labs/$Lab/web/server.py"

if (-not (Test-Path -LiteralPath $server)) {
    throw "Web demo server not found for lab: $Lab"
}

Push-Location $root
try {
    python $server --host $HostName --port $Port
}
finally {
    Pop-Location
}
