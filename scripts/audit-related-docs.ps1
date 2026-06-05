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
$roadmap = Read-RepoFile "roadmap.md"
$docsReadme = Read-RepoFile "docs/README.md"
$labsReadme = Read-RepoFile "labs/README.md"
$productReadme = Read-RepoFile "docs/product/README.md"
$productVision = Read-RepoFile "docs/product/personalized-investment-research-agent.md"
$labPlan = Read-RepoFile "docs/product/lab-plan.md"
$securityPlan = Read-RepoFile "docs/product/security-and-secrets.md"
$lab01Readme = Read-RepoFile "labs/01-strategy-intake/README.md"
$lab01Source = Read-RepoFile "labs/01-strategy-intake/src/strategy_intake.py"
$lab01Tests = Read-RepoFile "labs/01-strategy-intake/tests/test_strategy_intake.py"
$sharedCaseReadme = Read-RepoFile "labs/shared/investment_research_case/README.md"
$sharedStrategyRequest = Read-RepoFile "labs/shared/investment_research_case/strategy_request.md"
$sharedStrategyPolicy = Read-RepoFile "labs/shared/investment_research_case/strategy_policy.md"
$sharedRiskPolicy = Read-RepoFile "labs/shared/investment_research_case/risk_policy.md"
$sharedUserProfile = Read-RepoFile "labs/shared/investment_research_case/user_profile.md"
$envExample = Read-RepoFile ".env.example"
$gitignore = Read-RepoFile ".gitignore"
$secretCheck = Read-RepoFile "scripts/check-secrets.ps1"

$requiredDirectoryReadmes = @(
    "docs/readings/README.md",
    "docs/patterns/README.md",
    "docs/engineering/README.md",
    "docs/product/README.md",
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
if ($hook -notlike "*check-secrets.ps1*") {
    Add-Failure "hooks/content-update.md does not require check-secrets.ps1"
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

$requiredProductDocs = @(
    "docs/product/personalized-investment-research-agent.md",
    "docs/product/lab-plan.md",
    "docs/product/security-and-secrets.md"
)

foreach ($doc in $requiredProductDocs) {
    $null = Read-RepoFile $doc
    if ($readme -notlike "*$doc*") {
        Add-Failure "README.md does not link $doc"
    }
}

if ($docsReadme -notlike "*product/*") {
    Add-Failure "docs/README.md does not mention product/"
}
if ($productReadme -notlike "*personalized-investment-research-agent.md*" -or
    $productReadme -notlike "*lab-plan.md*" -or
    $productReadme -notlike "*security-and-secrets.md*") {
    Add-Failure "docs/product/README.md does not link all product docs"
}
if ($documentGraph -notlike "*product/personalized-investment-research-agent.md*" -or
    $documentGraph -notlike "*product/lab-plan.md*" -or
    $documentGraph -notlike "*product/security-and-secrets.md*") {
    Add-Failure "docs/document-graph.md does not map product docs"
}
if ($labsReadme -notlike "*lab-plan.md*" -or
    $labsReadme -notlike "*01-strategy-intake/README.md*" -or
    $labsReadme -notlike "*01-strategy-intake*" -or
    $labsReadme -notlike "*12-evaluation-safety*") {
    Add-Failure "labs/README.md does not describe the investment research lab route"
}
if ($labPlan -notlike "*Lab 01*" -or $labPlan -notlike "*Lab 12*" -or $labPlan -notlike "*mx-xuangu*") {
    Add-Failure "docs/product/lab-plan.md does not cover the full lab route or MX skills"
}
if ($productVision -notlike "*MIMO_API_KEY*" -or
    $productVision -notlike "*MX_APIKEY*" -or
    $productVision -notlike "*mx-xuangu*" -or
    $productVision -notlike "*mx-moni*") {
    Add-Failure "docs/product/personalized-investment-research-agent.md is missing model, data, or risk boundary"
}
if ($securityPlan -notlike "*MIMO_API_KEY*" -or
    $securityPlan -notlike "*MX_APIKEY*" -or
    $securityPlan -notlike "*check-secrets.ps1*" -or
    $securityPlan -notlike "*.env.example*") {
    Add-Failure "docs/product/security-and-secrets.md is missing required secret or safety guidance"
}
if ($envExample -notlike "*MIMO_API_KEY=your_mimo_api_key_from_hermes*" -or
    $envExample -notlike "*MX_APIKEY=your_mx_apikey_from_hermes*") {
    Add-Failure ".env.example is missing placeholder model or MX keys"
}
if ($gitignore -notlike "*!.env.example*") {
    Add-Failure ".gitignore does not allow .env.example"
}
if ($secretCheck -notlike "*git ls-files --cached --others --exclude-standard*" -or
    $secretCheck -notlike "*MIMO_API_KEY*" -or
    $secretCheck -notlike "*MX_APIKEY*") {
    Add-Failure "scripts/check-secrets.ps1 is missing expected scan behavior"
}
if ($roadmap -notlike "*Lab 01: Strategy Intake*" -or $todo -notlike "*Lab 02: Strategy Agent Loop*") {
    Add-Failure "roadmap.md or TODO.md does not reflect the investment research lab plan"
}
if ($roadmap -notlike "*x] Lab 01: Strategy Intake*" -or
    $todo -notlike "*Lab 01: Strategy Intake*") {
    Add-Failure "roadmap.md or TODO.md does not mark Lab 01 as complete"
}
if ($readme -notlike "*01-strategy-intake*" -or
    $documentGraph -notlike "*01-strategy-intake/README.md*" -or
    $labPlan -notlike "*labs/01-strategy-intake/*") {
    Add-Failure "README.md, docs/document-graph.md, or lab-plan.md does not link Lab 01"
}
if ($lab01Readme -notlike "*strategy_intake.py*" -or
    $lab01Readme -notlike "*unittest discover*" -or
    $lab01Readme -notlike "*StrategySpec*") {
    Add-Failure "labs/01-strategy-intake/README.md is missing run, test, or output guidance"
}
if ($lab01Source -notlike "*class StrategySpec*" -or
    $lab01Source -notlike "*parse_strategy_request*" -or
    $lab01Source -notlike "*RISK_DISCLOSURE*" -or
    $lab01Source -notlike "*PROHIBITED_PATTERNS*") {
    Add-Failure "Lab 01 source is missing StrategySpec, parser, risk disclosure, or prohibited patterns"
}
if ($lab01Tests -notlike "*test_default_case_parses_to_agent_spec*" -or
    $lab01Tests -notlike "*test_prohibited_request_gets_boundary_prompt*") {
    Add-Failure "Lab 01 tests do not cover default parsing and prohibited requests"
}
if ($sharedCaseReadme -notlike "*strategy_request.md*" -or
    $sharedCaseReadme -notlike "*risk_policy.md*" -or
    $sharedCaseReadme -notlike "*user_profile.md*") {
    Add-Failure "shared investment research case README does not list first-batch materials"
}
if ($sharedStrategyRequest -notlike "*Workflow*" -or
    $sharedStrategyPolicy -notlike "*StrategySpec*" -or
    $sharedRiskPolicy -notlike "*API Key*" -or
    $sharedUserProfile -notlike "*risk_level*") {
    Add-Failure "shared investment research case first-batch materials are incomplete"
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Output $_ }
    throw "Related docs audit failed."
}

Write-Output "Related docs audit passed."
