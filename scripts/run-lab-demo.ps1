param(
    [string]$Lab = "01-strategy-intake",
    [string]$Request = "",
    [string]$RequestsFile = "",
    [string]$Output = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$demo = Join-Path $root "labs/$Lab/demo/run_demo.py"

if (-not (Test-Path -LiteralPath $demo)) {
    throw "Demo runner not found for lab: $Lab"
}

$pythonArgs = @($demo)
if ($Request) {
    $pythonArgs += @("--request", $Request)
}
if ($RequestsFile) {
    $pythonArgs += @("--requests-file", $RequestsFile)
}
if ($Output) {
    $pythonArgs += @("--output", $Output)
}
if ($Json) {
    $pythonArgs += "--json"
}

Push-Location $root
try {
    python @pythonArgs
}
finally {
    Pop-Location
}
