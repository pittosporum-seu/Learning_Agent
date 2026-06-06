param(
    [string]$Lab = "01-strategy-intake",
    [int]$Port = 8765,
    [string]$HostName = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$server = Join-Path $root "labs/$Lab/web/server.py"

function Import-HermesXiaomiEnv {
    $candidateEnvFiles = @(
        "\\wsl.localhost\Ubuntu-24.04\home\pitto\.hermes\.env",
        "\\wsl.localhost\Ubuntu\home\pitto\.hermes\.env",
        (Join-Path $HOME ".hermes\.env")
    )

    foreach ($envFile in $candidateEnvFiles) {
        if (-not (Test-Path -LiteralPath $envFile)) {
            continue
        }

        $content = Get-Content -Encoding UTF8 -LiteralPath $envFile
        foreach ($line in $content) {
            if ($line -notmatch "^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)\s*$") {
                continue
            }

            $name = $Matches[1]
            $value = $Matches[2].Trim().Trim('"').Trim("'")
            if ($name -in @("XIAOMI_API_KEY", "XIAOMI_BASE_URL", "XIAOMI_MODEL")) {
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
        break
    }

    if ($env:XIAOMI_API_KEY) {
        Set-Item -Path Env:MIMO_API_KEY -Value $env:XIAOMI_API_KEY
    }
    if ($env:XIAOMI_BASE_URL) {
        Set-Item -Path Env:MIMO_BASE_URL -Value $env:XIAOMI_BASE_URL
    }
    if (-not $env:XIAOMI_MODEL) {
        Set-Item -Path Env:XIAOMI_MODEL -Value "mimo-v2.5"
    }
    if ($env:XIAOMI_MODEL) {
        Set-Item -Path Env:MIMO_MODEL -Value $env:XIAOMI_MODEL
    }
}

if (-not (Test-Path -LiteralPath $server)) {
    throw "Web demo server not found for lab: $Lab"
}

Push-Location $root
try {
    Import-HermesXiaomiEnv
    python $server --host $HostName --port $Port
}
finally {
    Pop-Location
}
