$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
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

function Require-Contains {
    param(
        [string]$Name,
        [string]$Content,
        [string[]]$Tokens
    )

    foreach ($token in $Tokens) {
        if (-not $Content.Contains($token)) {
            Add-Failure "$Name does not contain required token: $token"
        }
    }
}

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

$readme = Read-RepoFile "README.md"
$foundationsReadme = Read-RepoFile "docs/foundations/README.md"
$seriesPlan = Read-RepoFile "docs/series-plan.md"
$documentGraph = Read-RepoFile "docs/document-graph.md"
$resources = Read-RepoFile "resources/README.md"
$hook = Read-RepoFile "hooks/content-update.md"
$todo = Read-RepoFile "TODO.md"
$roadmap = Read-RepoFile "roadmap.md"
$docsReadme = Read-RepoFile "docs/README.md"
$startHere = Read-RepoFile "docs/start-here.md"
$glossary = Read-RepoFile "docs/glossary.md"
$labsReadme = Read-RepoFile "labs/README.md"
$productReadme = Read-RepoFile "docs/product/README.md"
$productVision = Read-RepoFile "docs/product/personalized-investment-research-agent.md"
$showcaseFramework = Read-RepoFile "docs/product/showcase-framework.md"
$labPlan = Read-RepoFile "docs/product/lab-plan.md"
$securityPlan = Read-RepoFile "docs/product/security-and-secrets.md"
$envExample = Read-RepoFile ".env.example"
$gitignore = Read-RepoFile ".gitignore"
$secretCheck = Read-RepoFile "scripts/check-secrets.ps1"
$runLabTests = Read-RepoFile "scripts/run-lab-tests.ps1"
$runLabDemo = Read-RepoFile "scripts/run-lab-demo.ps1"
$runLabWeb = Read-RepoFile "scripts/run-lab-web.ps1"
$rootAgents = Read-RepoFile "AGENTS.md"
$productAgents = Read-RepoFile "docs/product/AGENTS.md"
$labsAgents = Read-RepoFile "labs/AGENTS.md"
$lab01Agents = Read-RepoFile "labs/01-strategy-intake/AGENTS.md"
$lab02Agents = Read-RepoFile "labs/02-strategy-agent-loop/AGENTS.md"
$labImplementationSkill = Read-RepoFile ".agents/skills/lab-implementation/SKILL.md"
$docsSyncSkill = Read-RepoFile ".agents/skills/docs-sync/SKILL.md"
$codexRules = Read-RepoFile ".codex/rules/learning-agent.rules"

$lab01Readme = Read-RepoFile "labs/01-strategy-intake/README.md"
$lab01Source = Read-RepoFile "labs/01-strategy-intake/src/strategy_intake.py"
$lab01MimoSource = Read-RepoFile "labs/01-strategy-intake/src/mimo_strategy_intake.py"
$lab01LlmSource = Read-RepoFile "labs/01-strategy-intake/src/llm_strategy_intake.py"
$lab01Tests = Read-RepoFile "labs/01-strategy-intake/tests/test_strategy_intake.py"
$lab01LlmTests = Read-RepoFile "labs/01-strategy-intake/tests/test_llm_strategy_intake.py"
$lab01Demo = Read-RepoFile "labs/01-strategy-intake/demo/run_demo.py"
$lab01WebServer = Read-RepoFile "labs/01-strategy-intake/web/server.py"
$lab01WebIndex = Read-RepoFile "labs/01-strategy-intake/web/index.html"

$lab02Readme = Read-RepoFile "labs/02-strategy-agent-loop/README.md"
$lab02Source = Read-RepoFile "labs/02-strategy-agent-loop/src/agent_loop.py"
$lab02Tests = Read-RepoFile "labs/02-strategy-agent-loop/tests/test_agent_loop.py"
$lab02Demo = Read-RepoFile "labs/02-strategy-agent-loop/demo/run_demo.py"

$sharedCaseReadme = Read-RepoFile "labs/shared/investment_research_case/README.md"
$sharedStrategyRequest = Read-RepoFile "labs/shared/investment_research_case/strategy_request.md"
$sharedStrategyPolicy = Read-RepoFile "labs/shared/investment_research_case/strategy_policy.md"
$sharedRiskPolicy = Read-RepoFile "labs/shared/investment_research_case/risk_policy.md"
$sharedUserProfile = Read-RepoFile "labs/shared/investment_research_case/user_profile.md"
$sharedTestingReadme = Read-RepoFile "labs/shared/testing/README.md"
$sharedTestingRunner = Read-RepoFile "labs/shared/testing/run_lab_tests.py"

foreach ($doc in $foundationDocs) {
    $fullPath = Join-Path $root $doc
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Add-Failure "Missing foundation article: $doc"
    }

    $fileName = Split-Path $doc -Leaf
    Require-Contains "README.md" $readme @($doc)
    Require-Contains "docs/foundations/README.md" $foundationsReadme @($fileName)
    Require-Contains "docs/document-graph.md" $documentGraph @($fileName)
}

foreach ($index in 1..12) {
    $number = "{0:D2}" -f $index
    if ($seriesPlan -notmatch "\|\s*$number\s*\|") {
        Add-Failure "docs/series-plan.md is missing row $number"
    }
}

Require-Contains "README.md" $readme @(
    "docs/start-here.md",
    "docs/glossary.md",
    "docs/document-graph.md",
    "TODO.md",
    "docs/product/README.md",
    "docs/product/personalized-investment-research-agent.md",
    "docs/product/showcase-framework.md",
    "docs/product/lab-plan.md",
    "docs/product/security-and-secrets.md",
    "labs/01-strategy-intake/README.md",
    "labs/02-strategy-agent-loop/README.md",
    "AGENTS.md",
    ".agents/skills",
    "run-lab-web.ps1",
    "run-lab-tests.ps1"
)

Require-Contains "resources/README.md" $resources @("datawhalechina/Agent-Learning-Hub")
Require-Contains "docs/series-plan.md" $seriesPlan @("Agent-Learning-Hub")
Require-Contains "hooks/content-update.md" $hook @(
    "docs/start-here.md",
    "docs/glossary.md",
    "docs/product/showcase-framework.md",
    "audit-related-docs.ps1",
    "check-secrets.ps1",
    "run-lab-tests.ps1",
    "TODO.md",
    "AGENTS.md",
    "LLM_API_KEY",
    "MIMO_API_KEY"
)
Require-Contains "docs/document-graph.md" $documentGraph @(
    "start-here.md",
    "glossary.md",
    "TODO.md",
    "product/README.md",
    "product/showcase-framework.md",
    "labs/01-strategy-intake",
    "labs/02-strategy-agent-loop",
    "product/lab-plan.md",
    "product/security-and-secrets.md",
    "AGENTS.md",
    ".agents/skills",
    "run-lab-demo.ps1",
    "run-lab-web.ps1",
    "run-lab-tests.ps1"
)

if ($todo -notlike "*## Doing*" -or $todo -notlike "*## Next*" -or $todo -notlike "*## Backlog*" -or $todo -notlike "*## Done*") {
    Add-Failure "TODO.md is missing one of the required board sections"
}
Require-Contains "TODO.md" $todo @("P0", "structured trace", "Lab 03: Finance Tool Use Mock")
$roadmapTokens = @(
    '[x] P0',
    'Start Here',
    'Glossary',
    '[x] Lab 01: Strategy Intake',
    '[x] Lab 01:',
    'routing_decision',
    '[x] Lab 02: Strategy Agent Loop',
    '[ ] Lab 03: Finance Tool Use Mock',
    'Codex'
)
Require-Contains "roadmap.md" $roadmap $roadmapTokens

Require-Contains "docs/README.md" $docsReadme @("start-here.md", "glossary.md", "product/README.md", "product/showcase-framework.md", "product/", "product/AGENTS.md")
Require-Contains "docs/start-here.md" $startHere @(
    "Start Here",
    "Agent Loop",
    "Tool Use",
    "showcase-framework.md",
    "Lab 01",
    "Lab 02",
    "Lab 03",
    "routing_decision",
    "mock",
    "key",
    "run-lab-tests.ps1"
)
Require-Contains "docs/glossary.md" $glossary @(
    "Agent",
    "Workflow",
    "Agent Loop",
    "Tool Use",
    "RAG",
    "Memory",
    "MCP",
    "Harness",
    "Coding Agent",
    "Subagent",
    "Skill",
    "Browser Agent",
    "Computer Use Agent",
    "Evaluation",
    "Trace",
    "Guardrails",
    "HITL",
    "StrategySpec",
    "Evidence Store"
)
Require-Contains "docs/product/README.md" $productReadme @(
    "Start Here",
    "personalized-investment-research-agent.md",
    "showcase-framework.md",
    "lab-plan.md",
    "security-and-secrets.md",
    "routing_decision",
    "Lab 03-12",
    "SKILL.md",
    "API key"
)
Require-Contains "docs/product/showcase-framework.md" $showcaseFramework @(
    "Part 0 Showcase Overview",
    "Part 1 Strategy Intake & Router",
    "Part 2 Agent Loop & Structured Trace",
    "Part 3 Finance Tool Use Mock",
    "Part 12 Evaluation & Safety",
    "StrategySpec",
    "RoutingDecision",
    "TraceEvent",
    "ToolCall",
    "EvidenceItem",
    "SafetyDecision",
    "EvalResult",
    "required_human_confirmation",
    "risk_disclosure",
    "mock"
)
Require-Contains "docs/product/personalized-investment-research-agent.md" $productVision @(
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "LLM_MODEL",
    "MX_APIKEY",
    "mx-xuangu",
    "mx-moni"
)
Require-Contains "docs/product/lab-plan.md" $labPlan @(
    "showcase-framework.md",
    "Lab 01",
    "Lab 02",
    "Lab 12",
    "routing_decision",
    "OpenAI-compatible",
    "LLM_API_KEY",
    "mx-xuangu",
    "mx-search"
)
Require-Contains "docs/product/security-and-secrets.md" $securityPlan @(
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "LLM_MODEL",
    "LLM_CHAT_COMPLETIONS_URL",
    "MIMO_API_KEY",
    "XIAOMI_API_KEY",
    "XIAOMI_BASE_URL",
    "XIAOMI_MODEL",
    "MIMO_CHAT_COMPLETIONS_URL",
    "MX_APIKEY",
    "check-secrets.ps1",
    ".env.example"
)

Require-Contains ".env.example" $envExample @(
    "LLM_API_KEY=your_openai_compatible_api_key_from_trusted_runtime",
    "LLM_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1",
    "LLM_MODEL=mimo-v2.5",
    "MIMO_API_KEY=your_mimo_api_key_from_hermes",
    "XIAOMI_API_KEY=your_mimo_api_key_from_hermes",
    "XIAOMI_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1",
    "XIAOMI_MODEL=mimo-v2.5",
    "MX_APIKEY=your_mx_apikey_from_hermes"
)
Require-Contains ".gitignore" $gitignore @("!.env.example")
Require-Contains "scripts/check-secrets.ps1" $secretCheck @(
    "git ls-files --cached --others --exclude-standard",
    "LLM_API_KEY",
    "MIMO_API_KEY",
    "MX_APIKEY"
)

Require-Contains "labs/README.md" $labsReadme @(
    "showcase-framework.md",
    "01-strategy-intake/README.md",
    "02-strategy-agent-loop/README.md",
    "03-finance-tool-use-mock",
    "12-evaluation-safety",
    "run-lab-demo.ps1",
    "run-lab-web.ps1",
    "run-lab-tests.ps1"
)

Require-Contains "AGENTS.md" $rootAgents @(
    "Agent learning showcase",
    "docs/start-here.md",
    "docs/product/showcase-framework.md",
    "docs/product/lab-plan.md",
    "scripts/check-content.ps1",
    "Completion Report"
)
Require-Contains "docs/product/AGENTS.md" $productAgents @(
    "docs/product/lab-plan.md",
    "docs/product/security-and-secrets.md",
    "docs/product/showcase-framework.md",
    "showcase framework",
    "MX_APIKEY"
)
Require-Contains "labs/AGENTS.md" $labsAgents @(
    "mock-first",
    "README.md",
    "demo",
    "tests",
    "run-lab-tests.ps1"
)
Require-Contains "labs/01-strategy-intake/AGENTS.md" $lab01Agents @(
    "Strategy Intake + Workflow/Agent Router",
    "StrategySpec",
    "routing_decision",
    "Workflow:",
    "Blocked:"
)
Require-Contains "labs/02-strategy-agent-loop/AGENTS.md" $lab02Agents @(
    "Agent Loop + structured trace",
    "why_this_action",
    "guardrail_triggered",
    "next_action_hint",
    "max_turns"
)
Require-Contains ".agents/skills/lab-implementation/SKILL.md" $labImplementationSkill @(
    "name: lab-implementation",
    "description:",
    "docs/product/lab-plan.md",
    "run-lab-tests.ps1 -Lab <lab-folder>",
    "check-secrets.ps1"
)
Require-Contains ".agents/skills/docs-sync/SKILL.md" $docsSyncSkill @(
    "name: docs-sync",
    "description:",
    "docs/product/showcase-framework.md",
    "docs/document-graph.md",
    "resources/README.md",
    "audit-related-docs.ps1"
)
Require-Contains ".codex/rules/learning-agent.rules" $codexRules @(
    "AGENTS.md",
    "mock-first",
    "environment-gated",
    "run-lab-tests.ps1"
)

Require-Contains "labs/01-strategy-intake/README.md" $lab01Readme @(
    "StrategySpec",
    "Workflow/Agent Router",
    "routing_decision",
    "not_selected",
    "blocked",
    "LLM_API_KEY",
    "OpenAI-compatible",
    "/api/parse-stream",
    "strategy_intake.py",
    "demo/run_demo.py",
    "run-lab-demo.ps1",
    "run-lab-web.ps1",
    "127.0.0.1:8765",
    "run-lab-tests.ps1",
    "unittest discover"
)
Require-Contains "labs/01-strategy-intake/src/strategy_intake.py" $lab01Source @(
    "class StrategySpec",
    "class RoutingDecision",
    "build_routing_decision",
    "matched_signals",
    "parse_strategy_request",
    "RISK_DISCLOSURE",
    "PROHIBITED_PATTERNS"
)
Require-Contains "labs/01-strategy-intake/src/mimo_strategy_intake.py" $lab01MimoSource @(
    "parse_strategy_request_with_mimo",
    "parse_strategy_request_with_llm",
    "MimoConfig"
)
Require-Contains "labs/01-strategy-intake/src/llm_strategy_intake.py" $lab01LlmSource @(
    "DEFAULT_XIAOMI_CHAT_URL",
    "DEFAULT_PROVIDER_LABEL",
    "parse_strategy_request_with_llm",
    "LLMConfig",
    "routing_decision",
    "LLM_API_KEY",
    "api-key"
)
Require-Contains "labs/01-strategy-intake/tests/test_strategy_intake.py" $lab01Tests @(
    "test_default_case_parses_to_agent_spec",
    "test_simple_valuation_screen_is_workflow",
    "test_prohibited_request_gets_boundary_prompt",
    "routing_decision",
    "blocked"
)
Require-Contains "labs/01-strategy-intake/tests/test_llm_strategy_intake.py" $lab01LlmTests @(
    "fake_transport",
    "test_llm_response_merges_with_baseline_and_safety_fields",
    "test_env_config_uses_llm_values"
)
Require-Contains "labs/01-strategy-intake/tests/test_web_server.py" (Read-RepoFile "labs/01-strategy-intake/tests/test_web_server.py") @(
    "test_parse_stream_returns_stages_and_result",
    "/api/parse-stream"
)
Require-Contains "labs/01-strategy-intake/demo/run_demo.py" $lab01Demo @("build_demo_results", "--request", "--output", "routing_decision")
Require-Contains "labs/01-strategy-intake/web/server.py" $lab01WebServer @(
    "ThreadingHTTPServer",
    "/api/parse",
    "/api/parse-stream",
    '"stage": "route"',
    "parse_strategy_request_with_llm"
)
$lab01WebIndexTokens = @(
    "StrategySpec",
    "routing_decision",
    "routeValue",
    "matchedSignals",
    'fetch("/api/parse"',
    'fetch("/api/parse-stream"',
    'data-mode="llm"',
    'data-mode="rules"'
)
Require-Contains "labs/01-strategy-intake/web/index.html" $lab01WebIndex $lab01WebIndexTokens

Require-Contains "labs/02-strategy-agent-loop/README.md" $lab02Readme @(
    "Agent Loop",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1",
    "max_turns"
)
Require-Contains "labs/02-strategy-agent-loop/src/agent_loop.py" $lab02Source @(
    "run_strategy_agent_loop",
    "TraceEvent",
    "LoopState",
    "build_research_plan",
    "max_turns"
)
Require-Contains "labs/02-strategy-agent-loop/tests/test_agent_loop.py" $lab02Tests @(
    "test_agent_request_builds_multistep_research_plan",
    "test_max_turn_guardrail_can_fail_closed"
)
Require-Contains "labs/02-strategy-agent-loop/demo/run_demo.py" $lab02Demo @("run_strategy_agent_loop", "--request", "--output")

Require-Contains "labs/shared/testing/README.md" $sharedTestingReadme @("run_lab_tests.py")
Require-Contains "labs/shared/testing/run_lab_tests.py" $sharedTestingRunner @("unittest", "--lab")
Require-Contains "scripts/run-lab-tests.ps1" $runLabTests @("run_lab_tests.py")
Require-Contains "scripts/run-lab-demo.ps1" $runLabDemo @("run_demo.py")
Require-Contains "scripts/run-lab-web.ps1" $runLabWeb @("server.py", "HostName", "LLM_API_KEY", "LLM_CHAT_COMPLETIONS_URL")

Require-Contains "labs/shared/investment_research_case/README.md" $sharedCaseReadme @(
    "strategy_request.md",
    "risk_policy.md",
    "user_profile.md"
)
Require-Contains "labs/shared/investment_research_case/strategy_request.md" $sharedStrategyRequest @("Workflow")
Require-Contains "labs/shared/investment_research_case/strategy_policy.md" $sharedStrategyPolicy @("StrategySpec")
Require-Contains "labs/shared/investment_research_case/risk_policy.md" $sharedRiskPolicy @("API Key")
Require-Contains "labs/shared/investment_research_case/user_profile.md" $sharedUserProfile @("risk_level")

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Output $_ }
    throw "Related docs audit failed."
}

Write-Output "Related docs audit passed."
