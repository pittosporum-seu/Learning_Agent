param(
    [string]$Lab = "01-strategy-intake",
    [int]$Port = 8765,
    [string]$HostName = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$server = Join-Path $root "labs/$Lab/web/server.py"

function Import-HermesModelEnv {
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
            if ($name -in @(
                "LLM_API_KEY",
                "LLM_BASE_URL",
                "LLM_MODEL",
                "LLM_PROVIDER_LABEL",
                "LLM_CHAT_COMPLETIONS_URL",
                "XIAOMI_API_KEY",
                "XIAOMI_BASE_URL",
                "XIAOMI_MODEL",
                "XIAOMI_CHAT_COMPLETIONS_URL",
                "MIMO_API_KEY",
                "MIMO_BASE_URL",
                "MIMO_MODEL",
                "MIMO_CHAT_COMPLETIONS_URL"
            )) {
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
        break
    }

    if (-not $env:LLM_API_KEY -and $env:XIAOMI_API_KEY) {
        Set-Item -Path Env:LLM_API_KEY -Value $env:XIAOMI_API_KEY
    }
    if (-not $env:LLM_BASE_URL -and $env:XIAOMI_BASE_URL) {
        Set-Item -Path Env:LLM_BASE_URL -Value $env:XIAOMI_BASE_URL
    }
    if (-not $env:LLM_CHAT_COMPLETIONS_URL -and $env:XIAOMI_CHAT_COMPLETIONS_URL) {
        Set-Item -Path Env:LLM_CHAT_COMPLETIONS_URL -Value $env:XIAOMI_CHAT_COMPLETIONS_URL
    }
    if (-not $env:LLM_MODEL -and $env:XIAOMI_MODEL) {
        Set-Item -Path Env:LLM_MODEL -Value $env:XIAOMI_MODEL
    }
    if (-not $env:LLM_MODEL -and $env:XIAOMI_API_KEY) {
        Set-Item -Path Env:LLM_MODEL -Value "mimo-v2.5"
    }
    if (-not $env:LLM_PROVIDER_LABEL -and $env:XIAOMI_API_KEY) {
        Set-Item -Path Env:LLM_PROVIDER_LABEL -Value "Xiaomi MiMo"
    }
    if (-not $env:LLM_API_KEY -and $env:MIMO_API_KEY) {
        Set-Item -Path Env:LLM_API_KEY -Value $env:MIMO_API_KEY
    }
    if (-not $env:LLM_BASE_URL -and $env:MIMO_BASE_URL) {
        Set-Item -Path Env:LLM_BASE_URL -Value $env:MIMO_BASE_URL
    }
    if (-not $env:LLM_CHAT_COMPLETIONS_URL -and $env:MIMO_CHAT_COMPLETIONS_URL) {
        Set-Item -Path Env:LLM_CHAT_COMPLETIONS_URL -Value $env:MIMO_CHAT_COMPLETIONS_URL
    }
    if (-not $env:LLM_MODEL -and $env:MIMO_MODEL) {
        Set-Item -Path Env:LLM_MODEL -Value $env:MIMO_MODEL
    }
    if (-not $env:LLM_MODEL -and $env:MIMO_API_KEY) {
        Set-Item -Path Env:LLM_MODEL -Value "mimo-v2.5"
    }
    if (-not $env:LLM_PROVIDER_LABEL -and $env:MIMO_API_KEY) {
        Set-Item -Path Env:LLM_PROVIDER_LABEL -Value "Xiaomi MiMo"
    }

}

if (-not (Test-Path -LiteralPath $server)) {
    throw "Web demo server not found for lab: $Lab"
}

Push-Location $root
try {
    Import-HermesModelEnv
    python $server --host $HostName --port $Port
}
finally {
    Pop-Location
}
