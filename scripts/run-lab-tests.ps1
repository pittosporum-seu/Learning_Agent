param(
    [string]$Lab = "",
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $root "labs/shared/testing/run_lab_tests.py"

$pythonArgs = @($runner)
if ($Lab) {
    $pythonArgs += @("--lab", $Lab)
}
if ($VerboseOutput) {
    $pythonArgs += "--verbose"
}

Push-Location $root
try {
    python @pythonArgs
}
finally {
    Pop-Location
}
