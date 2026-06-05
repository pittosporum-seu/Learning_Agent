$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot

$foundationDocs = @(
    "docs/foundations/01-workflow-vs-agent.md",
    "docs/foundations/02-agent-loop.md",
    "docs/foundations/03-tool-use.md",
    "docs/foundations/04-rag.md",
    "docs/foundations/05-memory.md",
    "docs/foundations/06-mcp.md",
    "docs/foundations/07-agent-harness.md",
    "docs/foundations/08-coding-agent.md",
    "docs/foundations/09-subagent-multi-agent.md",
    "docs/foundations/10-skills.md",
    "docs/foundations/11-browser-computer-use-agent.md",
    "docs/foundations/12-evaluation-trace-safety.md"
)

$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message) | Out-Null
}

function Read-RepoFile {
    param([string]$RelativePath)
    $path = Join-Path $root $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Failure "Missing file: $RelativePath"
        return ""
    }
    return (Get-Content -Encoding UTF8 -LiteralPath $path) -join "`n"
}

$readme = Read-RepoFile "README.md"
$foundationsReadme = Read-RepoFile "docs/foundations/README.md"
$seriesPlan = Read-RepoFile "docs/series-plan.md"
$documentGraph = Read-RepoFile "docs/document-graph.md"
$resources = Read-RepoFile "resources/README.md"
$hook = Read-RepoFile "hooks/content-update.md"
$todo = Read-RepoFile "TODO.md"

$requiredDirectoryReadmes = @(
    "docs/readings/README.md",
    "docs/patterns/README.md",
    "docs/engineering/README.md",
    "skills/README.md"
)

foreach ($doc in $foundationDocs) {
    $fullPath = Join-Path $root $doc
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Add-Failure "Missing foundation article: $doc"
    }

    $fileName = Split-Path $doc -Leaf
    if ($readme -notlike "*$doc*") {
        Add-Failure "README.md does not link $doc"
    }
    if ($foundationsReadme -notlike "*$fileName*") {
        Add-Failure "docs/foundations/README.md does not list $fileName"
    }
    if ($documentGraph -notlike "*$fileName*") {
        Add-Failure "docs/document-graph.md does not map $fileName"
    }
}

foreach ($index in 1..12) {
    $number = "{0:D2}" -f $index
    if ($seriesPlan -notmatch "\|\s*$number\s*\|") {
        Add-Failure "docs/series-plan.md is missing row $number"
    }
}

if ($readme -notlike "*docs/document-graph.md*") {
    Add-Failure "README.md does not link docs/document-graph.md"
}
if ($readme -notlike "*TODO.md*") {
    Add-Failure "README.md does not link TODO.md"
}
if ($resources -notlike "*datawhalechina/Agent-Learning-Hub*") {
    Add-Failure "resources/README.md does not record Agent-Learning-Hub"
}
if ($seriesPlan -notlike "*Agent-Learning-Hub*") {
    Add-Failure "docs/series-plan.md does not mention Agent-Learning-Hub"
}
if ($hook -notlike "*audit-related-docs.ps1*") {
    Add-Failure "hooks/content-update.md does not require audit-related-docs.ps1"
}
if ($hook -notlike "*TODO.md*") {
    Add-Failure "hooks/content-update.md does not mention TODO.md"
}
if ($documentGraph -notlike "*TODO.md*") {
    Add-Failure "docs/document-graph.md does not mention TODO.md"
}
if ($todo -notlike "*## Doing*" -or $todo -notlike "*## Next*" -or $todo -notlike "*## Backlog*" -or $todo -notlike "*## Done*") {
    Add-Failure "TODO.md is missing one of the required board sections"
}

foreach ($doc in $requiredDirectoryReadmes) {
    $null = Read-RepoFile $doc
    $dirName = Split-Path (Split-Path $doc -Parent) -Leaf
    $directoryToken = if ($dirName -eq "skills") { "skills/" } else { "$dirName/" }
    if ($readme -notlike "*$directoryToken*") {
        Add-Failure "README.md does not include $directoryToken in the repository tree"
    }
    if ($documentGraph -notlike "*$dirName*") {
        Add-Failure "docs/document-graph.md does not mention $dirName"
    }
}

foreach ($dirName in @("readings", "patterns", "engineering")) {
    if ($seriesPlan -notlike "*$dirName*") {
        Add-Failure "docs/series-plan.md does not mention $dirName"
    }
}

if ($resources -notlike "*docs/readings/*") {
    Add-Failure "resources/README.md does not explain the relation with docs/readings"
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Output $_ }
    throw "Related docs audit failed."
}

Write-Output "Related docs audit passed."
