$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function New-TextFromCodePoint {
    param([int[]]$CodePoints)
    return -join ($CodePoints | ForEach-Object { [char]$_ })
}

$patterns = @(
    (New-TextFromCodePoint @(0x5199, 0x6587, 0x7AE0, 0x6CE8, 0x610F, 0x4E8B, 0x9879)),
    (New-TextFromCodePoint @(0x4EA4, 0x4ED8, 0x524D, 0x81EA, 0x68C0)),
    "utm_source=chatgpt",
    "chatgpt.com",
    (New-TextFromCodePoint @(0x4E0B, 0x4E00, 0x6B65, 0x53EF, 0x4EE5, 0x4ECE))
)

$root = Split-Path -Parent $PSScriptRoot
$markdownFiles = Get-ChildItem -Path $root -Recurse -Filter "*.md" |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\hooks\\"
    }

$matches = foreach ($file in $markdownFiles) {
    Select-String -Path $file.FullName -Pattern $patterns -SimpleMatch -Encoding UTF8 |
        ForEach-Object {
            [PSCustomObject]@{
                File = $_.Path
                Line = $_.LineNumber
                Text = $_.Line.Trim()
            }
        }
}

if ($matches) {
    $matches | Format-Table -AutoSize
    throw "Content check failed: remove process notes, chat traces, or tracking parameters."
}

Write-Output "Content check passed."
