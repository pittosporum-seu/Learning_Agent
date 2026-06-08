$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot

Push-Location $root
try {
    $files = git ls-files --cached --others --exclude-standard
}
finally {
    Pop-Location
}

$skipRelative = @(
    ".env.example",
    "scripts/check-secrets.ps1"
)

$skipPatterns = @(
    "^\.git/",
    "^node_modules/",
    "^dist/",
    "^build/",
    "^\.venv/",
    "^venv/"
)

$placeholderPattern = '(?i)^(your_|example|placeholder|changeme|todo|test|mock|dummy|<|$)'

$checks = @(
    @{
        Name = "real environment secret"
        Pattern = '(?i)\b(LLM_API_KEY|MIMO_API_KEY|MX_APIKEY|OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*[:=]\s*([^\s`"''>]+)'
        ValueGroup = 2
    },
    @{
        Name = "bearer token"
        Pattern = '(?i)\bBearer\s+([A-Za-z0-9._\-]{20,})'
        ValueGroup = 1
    },
    @{
        Name = "generic access token"
        Pattern = '(?i)\b(access_token|refresh_token|api_key|apikey|secret|password)\s*[:=]\s*([A-Za-z0-9._\-]{20,})'
        ValueGroup = 2
    },
    @{
        Name = "OpenAI-style key"
        Pattern = '\bsk-[A-Za-z0-9_\-]{20,}\b'
        ValueGroup = 0
    }
)

$findings = New-Object System.Collections.Generic.List[string]

foreach ($relativePath in $files) {
    if ([string]::IsNullOrWhiteSpace($relativePath)) {
        continue
    }

    $normalized = $relativePath -replace "\\", "/"
    if ($skipRelative -contains $normalized) {
        continue
    }

    $skip = $false
    foreach ($pattern in $skipPatterns) {
        if ($normalized -match $pattern) {
            $skip = $true
            break
        }
    }
    if ($skip) {
        continue
    }

    $path = Join-Path $root $relativePath
    if (-not (Test-Path -LiteralPath $path)) {
        continue
    }

    $item = Get-Item -LiteralPath $path
    if ($item.PSIsContainer -or $item.Length -gt 2MB) {
        continue
    }

    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $path
    foreach ($check in $checks) {
        $matches = [regex]::Matches($content, $check.Pattern)
        foreach ($match in $matches) {
            $value = if ($check.ValueGroup -gt 0) { $match.Groups[$check.ValueGroup].Value } else { $match.Value }
            if ($value -match $placeholderPattern) {
                continue
            }

            $lineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
            $findings.Add("${relativePath}:$lineNumber contains possible $($check.Name)") | Out-Null
        }
    }
}

if ($findings.Count -gt 0) {
    $findings | ForEach-Object { Write-Output $_ }
    throw "Secret check failed: remove real credentials or move them to a trusted local environment."
}

Write-Output "Secret check passed."
