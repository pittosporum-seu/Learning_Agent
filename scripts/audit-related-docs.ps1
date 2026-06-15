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

function Test-TextHasLabReference {
    param(
        [string]$Content,
        [string]$LabFolder,
        [string]$LabNumber
    )

    return $Content.Contains($LabFolder) -or
        $Content.Contains("Lab $LabNumber") -or
        $Content.Contains("Lab$LabNumber") -or
        $Content.Contains("Part $([int]$LabNumber)")
}

function Get-SectionBetween {
    param(
        [string]$Content,
        [string]$StartHeading,
        [string]$EndHeading
    )

    $pattern = "(?s)$([regex]::Escape($StartHeading))(.*?)$([regex]::Escape($EndHeading))"
    $match = [regex]::Match($Content, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return ""
}

function Test-RoadmapLabCompleted {
    param(
        [string]$Content,
        [string]$LabNumber
    )

    return $Content -match "(?m)^\s*-\s*\[x\]\s*Lab ${LabNumber}:"
}

function Get-LabPlanLine {
    param(
        [string]$Content,
        [string]$LabNumber
    )

    $match = [regex]::Match($Content, "(?m)^\|\s*$LabNumber\s*\|.*$")
    if ($match.Success) {
        return $match.Value
    }
    return ""
}

function Test-LabPlanStatusInProgress {
    param([string]$Line)

    $planned = -join ([char]0x8BA1, [char]0x5212, [char]0x4E2D)
    $enhancing = -join ([char]0x589E, [char]0x5F3A, [char]0x4E2D)
    $inProgress = -join ([char]0x8FDB, [char]0x884C, [char]0x4E2D)
    return $Line.Contains($planned) -or $Line.Contains($enhancing) -or $Line.Contains($inProgress)
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
    "docs/foundations/12-evaluation-trace-safety.md",
    "docs/foundations/13-loop-engineering.md"
)

$readme = Read-RepoFile "README.md"
$foundationsReadme = Read-RepoFile "docs/foundations/README.md"
$foundationLoopEngineering = Read-RepoFile "docs/foundations/13-loop-engineering.md"
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
$lab09Design = Read-RepoFile "docs/product/lab09-research-planner-dag-design.md"
$lab10Design = Read-RepoFile "docs/product/lab10-evidence-report-design.md"
$lab11Design = Read-RepoFile "docs/product/lab11-simulation-portfolio-design.md"
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
$skillTemplateReadme = Read-RepoFile "docs/maintenance/codex-skill-templates/README.md"
$labImplementationSkillTemplate = Read-RepoFile "docs/maintenance/codex-skill-templates/lab-implementation/SKILL.md"
$docsSyncSkillTemplate = Read-RepoFile "docs/maintenance/codex-skill-templates/docs-sync/SKILL.md"

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
$lab03Agents = Read-RepoFile "labs/03-finance-tool-use-mock/AGENTS.md"
$lab03Readme = Read-RepoFile "labs/03-finance-tool-use-mock/README.md"
$lab03FinanceTools = Read-RepoFile "labs/03-finance-tool-use-mock/src/finance_tools.py"
$lab03ToolRegistry = Read-RepoFile "labs/03-finance-tool-use-mock/src/tool_registry.py"
$lab03Evidence = Read-RepoFile "labs/03-finance-tool-use-mock/src/evidence.py"
$lab03RunLab = Read-RepoFile "labs/03-finance-tool-use-mock/src/run_lab.py"
$lab03Demo = Read-RepoFile "labs/03-finance-tool-use-mock/demo/run_demo.py"
$lab03FinanceToolTests = Read-RepoFile "labs/03-finance-tool-use-mock/tests/test_finance_tools.py"
$lab03ToolRegistryTests = Read-RepoFile "labs/03-finance-tool-use-mock/tests/test_tool_registry.py"
$lab03RunLabTests = Read-RepoFile "labs/03-finance-tool-use-mock/tests/test_run_lab.py"
$lab03MockUniverse = Read-RepoFile "labs/03-finance-tool-use-mock/data/mock_universe.csv"
$lab03MockPrices = Read-RepoFile "labs/03-finance-tool-use-mock/data/mock_prices.csv"
$lab03MockNews = Read-RepoFile "labs/03-finance-tool-use-mock/data/mock_news.md"
$lab04Agents = Read-RepoFile "labs/04-research-rag-basic/AGENTS.md"
$lab04Readme = Read-RepoFile "labs/04-research-rag-basic/README.md"
$lab04DocumentLoader = Read-RepoFile "labs/04-research-rag-basic/src/document_loader.py"
$lab04SimpleRetriever = Read-RepoFile "labs/04-research-rag-basic/src/simple_retriever.py"
$lab04RagContext = Read-RepoFile "labs/04-research-rag-basic/src/rag_context.py"
$lab04RunLab = Read-RepoFile "labs/04-research-rag-basic/src/run_lab.py"
$lab04Demo = Read-RepoFile "labs/04-research-rag-basic/demo/run_demo.py"
$lab04DocumentLoaderTests = Read-RepoFile "labs/04-research-rag-basic/tests/test_document_loader.py"
$lab04SimpleRetrieverTests = Read-RepoFile "labs/04-research-rag-basic/tests/test_simple_retriever.py"
$lab04RunLabTests = Read-RepoFile "labs/04-research-rag-basic/tests/test_run_lab.py"
$lab04StrategyPolicy = Read-RepoFile "labs/04-research-rag-basic/data/strategy_policy.md"
$lab04RiskPolicy = Read-RepoFile "labs/04-research-rag-basic/data/risk_policy.md"
$lab04ReportTemplate = Read-RepoFile "labs/04-research-rag-basic/data/report_template.md"
$lab05Agents = Read-RepoFile "labs/05-user-preference-memory/AGENTS.md"
$lab05Readme = Read-RepoFile "labs/05-user-preference-memory/README.md"
$lab05MemoryStore = Read-RepoFile "labs/05-user-preference-memory/src/memory_store.py"
$lab05PreferencePolicy = Read-RepoFile "labs/05-user-preference-memory/src/preference_policy.py"
$lab05RunLab = Read-RepoFile "labs/05-user-preference-memory/src/run_lab.py"
$lab05Demo = Read-RepoFile "labs/05-user-preference-memory/demo/run_demo.py"
$lab05MemoryStoreTests = Read-RepoFile "labs/05-user-preference-memory/tests/test_memory_store.py"
$lab05PreferencePolicyTests = Read-RepoFile "labs/05-user-preference-memory/tests/test_preference_policy.py"
$lab05RunLabTests = Read-RepoFile "labs/05-user-preference-memory/tests/test_run_lab.py"
$lab05MockPreferences = Read-RepoFile "labs/05-user-preference-memory/data/mock_user_preferences.json"
$lab05MemoryEvents = Read-RepoFile "labs/05-user-preference-memory/data/memory_events.jsonl"
$lab06Agents = Read-RepoFile "labs/06-skill-registry/AGENTS.md"
$lab06Readme = Read-RepoFile "labs/06-skill-registry/README.md"
$lab06MockSkills = Read-RepoFile "labs/06-skill-registry/data/mock_skills.json"
$lab06SkillRegistry = Read-RepoFile "labs/06-skill-registry/src/skill_registry.py"
$lab06SkillSelector = Read-RepoFile "labs/06-skill-registry/src/skill_selector.py"
$lab06RunLab = Read-RepoFile "labs/06-skill-registry/src/run_lab.py"
$lab06Demo = Read-RepoFile "labs/06-skill-registry/demo/run_demo.py"
$lab06SkillRegistryTests = Read-RepoFile "labs/06-skill-registry/tests/test_skill_registry.py"
$lab06SkillSelectorTests = Read-RepoFile "labs/06-skill-registry/tests/test_skill_selector.py"
$lab06RunLabTests = Read-RepoFile "labs/06-skill-registry/tests/test_run_lab.py"
$lab07Agents = Read-RepoFile "labs/07-skill-generation/AGENTS.md"
$lab07Readme = Read-RepoFile "labs/07-skill-generation/README.md"
$lab07DraftTemplate = Read-RepoFile "labs/07-skill-generation/data/skill_draft_template.md"
$lab07DraftBuilder = Read-RepoFile "labs/07-skill-generation/src/skill_draft_builder.py"
$lab07SafetyReview = Read-RepoFile "labs/07-skill-generation/src/skill_safety_review.py"
$lab07RunLab = Read-RepoFile "labs/07-skill-generation/src/run_lab.py"
$lab07Demo = Read-RepoFile "labs/07-skill-generation/demo/run_demo.py"
$lab07DraftBuilderTests = Read-RepoFile "labs/07-skill-generation/tests/test_skill_draft_builder.py"
$lab07SafetyReviewTests = Read-RepoFile "labs/07-skill-generation/tests/test_skill_safety_review.py"
$lab07RunLabTests = Read-RepoFile "labs/07-skill-generation/tests/test_run_lab.py"
$lab08Agents = Read-RepoFile "labs/08-mx-skills-adapter/AGENTS.md"
$lab08Readme = Read-RepoFile "labs/08-mx-skills-adapter/README.md"
$lab08Capabilities = Read-RepoFile "labs/08-mx-skills-adapter/data/adapter_capabilities.json"
$lab08Contract = Read-RepoFile "labs/08-mx-skills-adapter/src/adapter_contract.py"
$lab08MockAdapter = Read-RepoFile "labs/08-mx-skills-adapter/src/mock_mx_adapter.py"
$lab08RealAdapter = Read-RepoFile "labs/08-mx-skills-adapter/src/real_mx_adapter.py"
$lab08RealStub = Read-RepoFile "labs/08-mx-skills-adapter/src/real_mx_adapter_stub.py"
$lab08Registry = Read-RepoFile "labs/08-mx-skills-adapter/src/adapter_registry.py"
$lab08RunLab = Read-RepoFile "labs/08-mx-skills-adapter/src/run_lab.py"
$lab08Demo = Read-RepoFile "labs/08-mx-skills-adapter/demo/run_demo.py"
$lab08ContractTests = Read-RepoFile "labs/08-mx-skills-adapter/tests/test_adapter_contract.py"
$lab08MockAdapterTests = Read-RepoFile "labs/08-mx-skills-adapter/tests/test_mock_mx_adapter.py"
$lab08RealAdapterTests = Read-RepoFile "labs/08-mx-skills-adapter/tests/test_real_mx_adapter.py"
$lab08RealStubTests = Read-RepoFile "labs/08-mx-skills-adapter/tests/test_real_mx_adapter_stub.py"
$lab08RunLabTests = Read-RepoFile "labs/08-mx-skills-adapter/tests/test_run_lab.py"
$lab08ManualRealAdapterTest = Read-RepoFile "labs/08-mx-skills-adapter/tests/manual_test_real_mx_adapter.py"
$lab09Agents = Read-RepoFile "labs/09-research-planner/AGENTS.md"
$lab09Readme = Read-RepoFile "labs/09-research-planner/README.md"
$lab09PlannerTemplate = Read-RepoFile "labs/09-research-planner/data/planner_template.json"
$lab09DagModel = Read-RepoFile "labs/09-research-planner/src/dag_model.py"
$lab09PlannerBuilder = Read-RepoFile "labs/09-research-planner/src/planner_builder.py"
$lab09PlannerExecutor = Read-RepoFile "labs/09-research-planner/src/planner_executor.py"
$lab09RunLab = Read-RepoFile "labs/09-research-planner/src/run_lab.py"
$lab09Demo = Read-RepoFile "labs/09-research-planner/demo/run_demo.py"
$lab09DagModelTests = Read-RepoFile "labs/09-research-planner/tests/test_dag_model.py"
$lab09PlannerBuilderTests = Read-RepoFile "labs/09-research-planner/tests/test_planner_builder.py"
$lab09PlannerExecutorTests = Read-RepoFile "labs/09-research-planner/tests/test_planner_executor.py"
$lab09RunLabTests = Read-RepoFile "labs/09-research-planner/tests/test_run_lab.py"
$lab10Agents = Read-RepoFile "labs/10-evidence-report/AGENTS.md"
$lab10Readme = Read-RepoFile "labs/10-evidence-report/README.md"
$lab10Template = Read-RepoFile "labs/10-evidence-report/data/report_template.json"
$lab10ReportModel = Read-RepoFile "labs/10-evidence-report/src/report_model.py"
$lab10EvidenceCollector = Read-RepoFile "labs/10-evidence-report/src/evidence_collector.py"
$lab10ReportBuilder = Read-RepoFile "labs/10-evidence-report/src/report_builder.py"
$lab10ReportSafety = Read-RepoFile "labs/10-evidence-report/src/report_safety.py"
$lab10RunLab = Read-RepoFile "labs/10-evidence-report/src/run_lab.py"
$lab10Demo = Read-RepoFile "labs/10-evidence-report/demo/run_demo.py"
$lab10ReportModelTests = Read-RepoFile "labs/10-evidence-report/tests/test_report_model.py"
$lab10EvidenceCollectorTests = Read-RepoFile "labs/10-evidence-report/tests/test_evidence_collector.py"
$lab10ReportBuilderTests = Read-RepoFile "labs/10-evidence-report/tests/test_report_builder.py"
$lab10ReportSafetyTests = Read-RepoFile "labs/10-evidence-report/tests/test_report_safety.py"
$lab10RunLabTests = Read-RepoFile "labs/10-evidence-report/tests/test_run_lab.py"

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

foreach ($index in 1..13) {
    $number = "{0:D2}" -f $index
    if ($seriesPlan -notmatch "\|\s*$number\s*\|") {
        Add-Failure "docs/series-plan.md is missing row $number"
    }
}

Require-Contains "docs/foundations/13-loop-engineering.md" $foundationLoopEngineering @(
    "Loop Engineering",
    "Prompt Engineering",
    "Trigger / Scheduler",
    "Context Loading",
    "Verifier / Evaluation",
    "Memory / State",
    "Stop Condition",
    "Human Review",
    "Cost / Budget",
    "Lab 10 Evidence Report",
    "mermaid",
    "datawhalechina/Agent-Learning-Hub"
)

Require-Contains "README.md" $readme @(
    "docs/start-here.md",
    "docs/glossary.md",
    "docs/document-graph.md",
    "TODO.md",
    "docs/product/README.md",
    "docs/product/personalized-investment-research-agent.md",
    "docs/product/showcase-framework.md",
    "docs/product/lab-plan.md",
    "docs/product/lab09-research-planner-dag-design.md",
    "docs/product/lab10-evidence-report-design.md",
    "docs/product/lab11-simulation-portfolio-design.md",
    "docs/product/security-and-secrets.md",
    "labs/01-strategy-intake/README.md",
    "labs/02-strategy-agent-loop/README.md",
    "labs/03-finance-tool-use-mock/README.md",
    "labs/04-research-rag-basic/README.md",
    "labs/05-user-preference-memory/README.md",
    "labs/09-research-planner/README.md",
    "labs/10-evidence-report/README.md",
    "AGENTS.md",
    "docs/maintenance/codex-skill-templates",
    "run-lab-web.ps1",
    "run-lab-tests.ps1"
)

Require-Contains "resources/README.md" $resources @("datawhalechina/Agent-Learning-Hub", "Loop Engineering")
Require-Contains "docs/series-plan.md" $seriesPlan @("Agent-Learning-Hub", "13", "Loop Engineering")
Require-Contains "hooks/content-update.md" $hook @(
    "docs/start-here.md",
    "docs/glossary.md",
    "docs/product/showcase-framework.md",
    "docs/product/lab09-research-planner-dag-design.md",
    "docs/product/lab10-evidence-report-design.md",
    "docs/product/lab11-simulation-portfolio-design.md",
    "docs/maintenance/codex-skill-templates/",
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
    "product/lab09-research-planner-dag-design.md",
    "product/lab10-evidence-report-design.md",
    "product/lab11-simulation-portfolio-design.md",
    "labs/01-strategy-intake",
    "labs/02-strategy-agent-loop",
    "labs/03-finance-tool-use-mock",
    "labs/04-research-rag-basic",
    "labs/05-user-preference-memory",
    "labs/09-research-planner",
    "labs/10-evidence-report",
    "product/lab-plan.md",
    "product/security-and-secrets.md",
    "AGENTS.md",
    "maintenance/codex-skill-templates",
    "run-lab-demo.ps1",
    "run-lab-web.ps1",
    "run-lab-tests.ps1"
)

if ($todo -notlike "*## Doing*" -or $todo -notlike "*## Next*" -or $todo -notlike "*## Backlog*" -or $todo -notlike "*## Done*") {
    Add-Failure "TODO.md is missing one of the required board sections"
}
Require-Contains "TODO.md" $todo @("P0", "structured trace", "Lab 03: Finance Tool Use Mock", "Lab 04: Research RAG Basic", "Lab 05: User Preference Memory", "Lab 06: Skill Registry", "Lab 07: Skill Generation", "Lab 08: Finance Provider Adapter", "Lab 09 Research Planner DAG", "Lab 09: Research Planner DAG", "Lab 10 Evidence Report", "Lab 10: Evidence Report", "Lab 11 Simulation Portfolio", "Lab 12 Evaluation & Safety", "Lab 08 optional external provider integration", "13 Loop Engineering")
$roadmapTokens = @(
    '[x] P0',
    'Start Here',
    'Glossary',
    '[x] Lab 01: Strategy Intake',
    '[x] Lab 01:',
    'routing_decision',
    '[x] Lab 02: Strategy Agent Loop',
    '[x] Lab 03: Finance Tool Use Mock',
    '[x] Lab 04: Research RAG Basic',
    '[x] Lab 05: User Preference Memory',
    '[x] Lab 06: Skill Registry',
    '[x] Lab 07: Skill Generation',
    '[x] Lab 08: Finance Provider Adapter',
    '[x] Lab 08: optional external provider manual integration',
    '[x] Lab 09: Research Planner',
    'Lab 10 Evidence Report',
    '[x] Lab 10: Evidence Report',
    'Simulation Portfolio Lab',
    '[ ] Lab 11: Simulation Portfolio',
    'Loop Engineering',
    'Skill'
)
Require-Contains "roadmap.md" $roadmap $roadmapTokens

$todoDoingSection = Get-SectionBetween $todo "## Doing" "## Next"
foreach ($index in 1..12) {
    $labNumber = "{0:D2}" -f $index
    $labPlanLine = Get-LabPlanLine $labPlan $labNumber
    $roadmapCompleted = Test-RoadmapLabCompleted $roadmap $labNumber

    if ($roadmapCompleted -and (Test-LabPlanStatusInProgress $labPlanLine)) {
        Add-Failure "Lab $labNumber is completed in roadmap.md but docs/product/lab-plan.md still has an in-progress status: $labPlanLine"
    }

    if ($todoDoingSection -match "Lab $labNumber") {
        if ($roadmapCompleted) {
            Add-Failure "TODO.md Doing still references completed Lab $labNumber"
        }
        elseif (-not (Test-LabPlanStatusInProgress $labPlanLine)) {
            Add-Failure "TODO.md Doing references Lab $labNumber but docs/product/lab-plan.md is not marked planned, enhancing, or in-progress: $labPlanLine"
        }
    }
}

Require-Contains "docs/README.md" $docsReadme @("start-here.md", "glossary.md", "product/README.md", "product/showcase-framework.md", "product/lab09-research-planner-dag-design.md", "product/lab10-evidence-report-design.md", "product/lab11-simulation-portfolio-design.md", "product/", "product/AGENTS.md", "maintenance/codex-skill-templates")
Require-Contains "docs/start-here.md" $startHere @(
    "Start Here",
    "Agent Loop",
    "Tool Use",
    "Loop Engineering",
    "foundations/13-loop-engineering.md",
    "showcase-framework.md",
    "Lab 01",
    "Lab 02",
    "Lab 03",
    "Lab 04",
    "Lab 05",
    "Lab 06",
    "Lab 07",
    "Lab 08",
    "Lab 09",
    "Lab 10",
    "lab09-research-planner-dag-design.md",
    "lab10-evidence-report-design.md",
    "planner_trace",
    "report_generation_trace",
    "evidence_refs",
    "human_review_gate",
    "routing_decision",
    "retrieved_context",
    "memory_trace",
    "skill_selection_trace",
    "draft_review",
    "adapter_trace",
    "safety_gate",
    "mock",
    "key",
    "run-lab-tests.ps1"
)
Require-Contains "docs/glossary.md" $glossary @(
    "Agent",
    "Workflow",
    "Agent Loop",
    "Loop Engineering",
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
    "13-loop-engineering.md",
    "lab09-research-planner-dag-design.md",
    "lab10-evidence-report-design.md",
    "lab11-simulation-portfolio-design.md",
    "security-and-secrets.md",
    "routing_decision",
    "tool_trace",
    "candidate_evidence",
    "retrieved_context",
    "memory_trace",
    "preference_adjusted_evidence",
    "skill_selection_trace",
    "draft_review",
    "adapter_trace",
    "safety_gate",
    "planner_trace",
    "report_generation_trace",
    "evidence_report",
    "evidence_refs",
    "human_review_gate",
    "Lab 03-12",
    "SKILL.md",
    "API key"
)
Require-Contains "docs/product/showcase-framework.md" $showcaseFramework @(
    "Part 0 Showcase Overview",
    "Loop Engineering",
    "13-loop-engineering.md",
    "Part 1 Strategy Intake & Router",
    "Part 2 Agent Loop & Structured Trace",
    "Part 3 Finance Tool Use Mock",
    "Part 4 Research RAG Basic",
    "Part 5 User Preference Memory",
    "Part 6 Skill Registry",
    "Part 7 Skill Generation",
    "Part 8 Finance Provider Adapter",
    "Part 9 Research Planner DAG",
    "lab09-research-planner-dag-design.md",
    "planner_trace",
    "human_review_gate",
    "Part 10 Evidence Report",
    "lab10-evidence-report-design.md",
    "report_generation_trace",
    "Part 11 Simulation Portfolio",
    "lab11-simulation-portfolio-design.md",
    "simulation_trace",
    "human_confirmation_gate",
    "Part 12 Evaluation & Safety",
    "StrategySpec",
    "RoutingDecision",
    "TraceEvent",
    "ToolCall",
    "EvidenceItem",
    "retrieved_context",
    "preference_adjusted_evidence",
    "skill_selection_trace",
    "skill_draft_markdown",
    "draft_review",
    "adapter_trace",
    "safety_gate",
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
    "tool_trace",
    "candidate_evidence",
    "retrieved_context",
    "preference_adjusted_evidence",
    "skill_selection_trace",
    "draft_review",
    "adapter_trace",
    "safety_gate",
    "planner_trace",
    "human_review_gate",
    "routing_decision",
    "OpenAI-compatible",
    "LLM_API_KEY",
    "candidate-screen",
    "finance-news",
    "evidence_report",
    "report_generation_trace",
    "lab09-research-planner-dag-design.md",
    "lab10-evidence-report-design.md",
    "lab11-simulation-portfolio-design.md"
)
Require-Contains "docs/product/lab09-research-planner-dag-design.md" $lab09Design @(
    "Research Planner DAG",
    "parse_and_route",
    "adapter_capability_check",
    "candidate_generation",
    "market_data_check",
    "news_risk_check",
    "evidence_context_attach",
    "memory_preference_adjustment",
    "skill_selection",
    "human_review_gate",
    "ResearchDagNode",
    "PlannerTraceEvent",
    "PlannerRunState",
    "HumanReviewGate",
    "PlannerFinalOutput",
    "planner_trace",
    "risk_disclosure",
    "safety_gate",
    "Lab 10 Evidence Report",
    "buy",
    "sell",
    "recommendation",
    "target_price"
)
Require-Contains "docs/product/lab10-evidence-report-design.md" $lab10Design @(
    "Evidence Report",
    "EvidenceReport",
    "ReportSection",
    "EvidenceReference",
    "CandidateObservation",
    "RiskAndLimitation",
    "HumanReviewChecklist",
    "ReportGenerationTrace",
    "report_generation_trace",
    "risk_disclosure",
    "human_review_required",
    "evidence_gaps",
    "adapter_trace",
    "candidate_evidence",
    "retrieved_context",
    "planner_trace",
    "Lab 11 Simulation Portfolio",
    "buy",
    "sell",
    "recommendation",
    "target_price"
)
Require-Contains "docs/product/lab11-simulation-portfolio-design.md" $lab11Design @(
    "Simulation Portfolio",
    "SimulationPortfolio",
    "SimulationProposal",
    "SimulationPosition",
    "SimulationAction",
    "HumanConfirmationGate",
    "SimulationTraceEvent",
    "SimulationSafetyReview",
    "waiting_human_confirmation",
    "confirmed_mock",
    "evidence_refs",
    "risk_disclosure",
    "mock_data_notice",
    "no_real_trade_notice",
    "human_review_required",
    "human_confirmation_gate",
    "Lab 12 Evaluation & Safety",
    "buy",
    "sell",
    "recommendation",
    "target_price"
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
    "FINANCE_PROVIDER_API_KEY",
    "FINANCE_PROVIDER_ALLOW_REAL",
    "FINANCE_PROVIDER_BASE_URL",
    "FINANCE_PROVIDER_PROFILE",
    "MX_APIKEY",
    "MX_SKILLS_BASE_URL",
    "MX_BASE_URL",
    "MX_ALLOW_REAL_PROVIDER",
    "raw_response_persisted=false",
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
    "FINANCE_PROVIDER_PROFILE=mx-skills",
    "FINANCE_PROVIDER_API_KEY=your_finance_provider_api_key_from_trusted_runtime",
    "FINANCE_PROVIDER_BASE_URL=https://mkapi2.dfcfs.com/finskillshub/api/claw",
    "FINANCE_PROVIDER_ALLOW_REAL=false",
    "FINANCE_PROVIDER_DOWNLOAD_URL=https://dl.dfcfs.com/m/itc4",
    "MX_APIKEY=your_mx_apikey_from_trusted_runtime",
    "MX_SKILLS_BASE_URL=https://mkapi2.dfcfs.com/finskillshub",
    "MX_ALLOW_REAL_PROVIDER=false",
    "MX_TIMEOUT_SECONDS=10"
)
Require-Contains ".gitignore" $gitignore @(
    "!.env.example",
    ".codex/",
    ".agents/",
    "*.local.json",
    "*.local.yaml",
    "*.local.yml",
    "runtime_config.json",
    "runtime_config.yaml",
    "runtime_config.*",
    "real_user_preferences.*",
    "real_memory_events.*",
    "provider_responses/",
    "authenticated_responses/",
    "labs/**/outputs/*",
    "!labs/**/outputs/.gitkeep"
)

$trackedFiles = & git -C $root ls-files
$trackedLocalRuntimeFiles = $trackedFiles | Where-Object {
    $_ -like ".agents/*" -or
    $_ -like ".codex/*" -or
    $_ -like "provider_responses/*" -or
    $_ -like "authenticated_responses/*" -or
    (($_ -like "labs/*/outputs/*") -and ($_ -notlike "labs/*/outputs/.gitkeep"))
}
foreach ($trackedLocalRuntimeFile in $trackedLocalRuntimeFiles) {
    Add-Failure "Tracked local runtime config must not be committed: $trackedLocalRuntimeFile"
}

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
    "03-finance-tool-use-mock/README.md",
    "04-research-rag-basic/README.md",
    "05-user-preference-memory/README.md",
    "06-skill-registry/README.md",
    "07-skill-generation/README.md",
    "08-mx-skills-adapter/README.md",
    "09-research-planner/README.md",
    "10-evidence-report/README.md",
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
Require-Contains "docs/maintenance/codex-skill-templates/README.md" $skillTemplateReadme @(
    "documentation template",
    "not local runtime configuration",
    "Lab Implementation",
    "Docs Sync"
)
Require-Contains "docs/maintenance/codex-skill-templates/lab-implementation/SKILL.md" $labImplementationSkillTemplate @(
    "name: lab-implementation",
    "description:",
    "documentation template",
    "docs/product/lab-plan.md",
    "run-lab-tests.ps1 -Lab <lab-folder>",
    "check-secrets.ps1"
)
Require-Contains "docs/maintenance/codex-skill-templates/docs-sync/SKILL.md" $docsSyncSkillTemplate @(
    "name: docs-sync",
    "description:",
    "documentation template",
    "docs/product/showcase-framework.md",
    "docs/document-graph.md",
    "resources/README.md",
    "audit-related-docs.ps1"
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
    "why_this_action",
    "guardrail_triggered",
    "next_action_hint",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1",
    "max_turns"
)
Require-Contains "labs/02-strategy-agent-loop/src/agent_loop.py" $lab02Source @(
    "run_strategy_agent_loop",
    "TraceEvent",
    "why_this_action",
    "guardrail_triggered",
    "next_action_hint",
    "plan_step_count",
    "guardrail_was_triggered",
    "LoopState",
    "build_research_plan",
    "max_turns"
)
Require-Contains "labs/02-strategy-agent-loop/tests/test_agent_loop.py" $lab02Tests @(
    "test_agent_request_builds_multistep_research_plan",
    "assert_structured_trace",
    "plan_step_count",
    "test_max_turn_guardrail_can_fail_closed"
)
Require-Contains "labs/02-strategy-agent-loop/demo/run_demo.py" $lab02Demo @("run_strategy_agent_loop", "--request", "--output")

Require-Contains "labs/03-finance-tool-use-mock/AGENTS.md" $lab03Agents @(
    "Tool Use",
    "mock finance tools",
    "tool_trace",
    "candidate_evidence",
    "risk_disclosure"
)
Require-Contains "labs/03-finance-tool-use-mock/README.md" $lab03Readme @(
    "Tool Use",
    "select_candidates",
    "fetch_market_data",
    "search_finance_news",
    "tool_trace",
    "candidate_evidence",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1"
)
Require-Contains "labs/03-finance-tool-use-mock/src/finance_tools.py" $lab03FinanceTools @(
    "select_candidates",
    "fetch_market_data",
    "search_finance_news",
    "mock_universe.csv",
    "mock_prices.csv",
    "mock_news.md"
)
Require-Contains "labs/03-finance-tool-use-mock/src/tool_registry.py" $lab03ToolRegistry @(
    "ToolRegistry",
    "ToolDefinition",
    "select_candidates",
    "fetch_market_data",
    "search_finance_news"
)
Require-Contains "labs/03-finance-tool-use-mock/src/evidence.py" $lab03Evidence @(
    "build_candidate_evidence",
    "evidence_items",
    "risk_flags"
)
Require-Contains "labs/03-finance-tool-use-mock/src/run_lab.py" $lab03RunLab @(
    "run_finance_tool_use_mock",
    "tool_trace",
    "candidate_evidence",
    "risk_disclosure",
    "Lab 04 Research RAG Basic",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/03-finance-tool-use-mock/demo/run_demo.py" $lab03Demo @(
    "run_finance_tool_use_mock",
    "--request",
    "--output",
    "tool_trace"
)
Require-Contains "labs/03-finance-tool-use-mock/tests/test_finance_tools.py" $lab03FinanceToolTests @(
    "test_select_candidates_filters_mock_grid_equipment",
    "test_fetch_market_data_returns_trend_and_drawdown",
    "test_search_finance_news_returns_risk_flags"
)
Require-Contains "labs/03-finance-tool-use-mock/tests/test_tool_registry.py" $lab03ToolRegistryTests @(
    "test_registry_contains_three_mock_tools",
    "select_candidates",
    "fetch_market_data",
    "search_finance_news"
)
Require-Contains "labs/03-finance-tool-use-mock/tests/test_run_lab.py" $lab03RunLabTests @(
    "test_run_lab_generates_tool_trace_and_candidate_evidence",
    "test_blocked_request_does_not_call_tools",
    "risk_disclosure",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/03-finance-tool-use-mock/data/mock_universe.csv" $lab03MockUniverse @("MXGRID001", "theme")
Require-Contains "labs/03-finance-tool-use-mock/data/mock_prices.csv" $lab03MockPrices @("trend_score", "max_drawdown")
Require-Contains "labs/03-finance-tool-use-mock/data/mock_news.md" $lab03MockNews @("risk_flags", "MXGRID001")

Require-Contains "labs/04-research-rag-basic/AGENTS.md" $lab04Agents @(
    "Research RAG Basic",
    "local mock documents",
    "retrieval_trace",
    "retrieved_context",
    "risk_disclosure"
)
Require-Contains "labs/04-research-rag-basic/README.md" $lab04Readme @(
    "RAG",
    "candidate_evidence",
    "retrieval_trace",
    "retrieved_context",
    "augmented_evidence",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1"
)
Require-Contains "labs/04-research-rag-basic/src/document_loader.py" $lab04DocumentLoader @(
    "load_documents",
    "load_markdown_chunks",
    "chunk_id",
    "source",
    "keywords"
)
Require-Contains "labs/04-research-rag-basic/src/simple_retriever.py" $lab04SimpleRetriever @(
    "retrieve",
    "matched_terms",
    "score",
    "top_k"
)
Require-Contains "labs/04-research-rag-basic/src/rag_context.py" $lab04RagContext @(
    "build_rag_context",
    "build_retrieval_query",
    "retrieval_trace",
    "retrieved_context",
    "used_for",
    "augmented_evidence"
)
Require-Contains "labs/04-research-rag-basic/src/run_lab.py" $lab04RunLab @(
    "run_research_rag_basic",
    "run_finance_tool_use_mock",
    "retrieval_trace",
    "retrieved_context",
    "Lab 05 User Preference Memory",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/04-research-rag-basic/demo/run_demo.py" $lab04Demo @(
    "run_research_rag_basic",
    "--request",
    "--output",
    "retrieved_context"
)
Require-Contains "labs/04-research-rag-basic/tests/test_document_loader.py" $lab04DocumentLoaderTests @(
    "test_load_documents_splits_markdown_into_chunks",
    "risk_policy.md",
    "report_template.md"
)
Require-Contains "labs/04-research-rag-basic/tests/test_simple_retriever.py" $lab04SimpleRetrieverTests @(
    "test_retriever_can_hit_risk_policy_and_report_template",
    "risk_policy.md",
    "report_template.md"
)
Require-Contains "labs/04-research-rag-basic/tests/test_run_lab.py" $lab04RunLabTests @(
    "test_run_lab_generates_retrieved_context_and_trace",
    "test_each_retrieved_context_has_required_fields",
    "test_blocked_request_skips_normal_retrieval",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/04-research-rag-basic/data/strategy_policy.md" $lab04StrategyPolicy @("StrategySpec", "candidate_evidence", "retrieved_context")
Require-Contains "labs/04-research-rag-basic/data/risk_policy.md" $lab04RiskPolicy @("risk_disclosure", "negative_news", "human_confirmation")
Require-Contains "labs/04-research-rag-basic/data/report_template.md" $lab04ReportTemplate @("report_template", "source", "chunk_id", "used_for")

Require-Contains "labs/05-user-preference-memory/AGENTS.md" $lab05Agents @(
    "User Preference Memory",
    "Memory",
    "memory_snapshot",
    "memory_trace",
    "preference_adjusted_evidence",
    "risk_disclosure"
)
Require-Contains "labs/05-user-preference-memory/README.md" $lab05Readme @(
    "Memory",
    "memory_snapshot",
    "memory_trace",
    "effective_user_profile",
    "preference_application",
    "preference_adjusted_evidence",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1"
)
Require-Contains "labs/05-user-preference-memory/src/memory_store.py" $lab05MemoryStore @(
    "build_memory_snapshot",
    "load_user_preferences",
    "load_memory_events",
    "UnknownUserError",
    "mock_user_preferences.json",
    "memory_events.jsonl"
)
Require-Contains "labs/05-user-preference-memory/src/preference_policy.py" $lab05PreferencePolicy @(
    "build_effective_user_profile",
    "apply_preferences",
    "SUPPORTED_FIELDS",
    "DANGEROUS_FIELDS",
    "preference_adjusted_evidence",
    "risk_disclosure"
)
Require-Contains "labs/05-user-preference-memory/src/run_lab.py" $lab05RunLab @(
    "run_user_preference_memory",
    "run_research_rag_basic",
    "memory_snapshot",
    "memory_trace",
    "preference_application",
    "preference_adjusted_evidence",
    "Lab 06 Skill Registry",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/05-user-preference-memory/demo/run_demo.py" $lab05Demo @(
    "run_user_preference_memory",
    "--user-id",
    "--output",
    "preference_application"
)
Require-Contains "labs/05-user-preference-memory/tests/test_memory_store.py" $lab05MemoryStoreTests @(
    "test_loads_conservative_and_balanced_users",
    "test_unknown_user_raises_clear_error",
    "conservative_user",
    "balanced_user"
)
Require-Contains "labs/05-user-preference-memory/tests/test_preference_policy.py" $lab05PreferencePolicyTests @(
    "test_effective_user_profile_applies_max_candidates",
    "test_apply_preferences_filters_excluded_risk_flags",
    "test_apply_preferences_does_not_mutate_original_evidence",
    "test_dangerous_preferences_are_ignored"
)
Require-Contains "labs/05-user-preference-memory/tests/test_run_lab.py" $lab05RunLabTests @(
    "test_run_lab_generates_memory_outputs",
    "test_original_candidate_evidence_is_not_modified",
    "test_blocked_request_remains_blocked",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/05-user-preference-memory/data/mock_user_preferences.json" $lab05MockPreferences @(
    "conservative_user",
    "balanced_user",
    "excluded_risk_flags",
    "report_style"
)
Require-Contains "labs/05-user-preference-memory/data/memory_events.jsonl" $lab05MemoryEvents @(
    "preference_update",
    "unsafe_preference_attempt",
    "risk_disclosure"
)

Require-Contains "labs/06-skill-registry/AGENTS.md" $lab06Agents @(
    "Skill Registry",
    "mock Skill",
    "skill_selection_trace",
    "selected_skills",
    "disabled_skills",
    "risk_disclosure"
)
Require-Contains "labs/06-skill-registry/README.md" $lab06Readme @(
    "Skill Registry",
    ".agents/",
    ".codex/",
    "skill_selection_trace",
    "selected_skills",
    "disabled_skills",
    "requires_human_confirmation",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1"
)
Require-Contains "labs/06-skill-registry/data/mock_skills.json" $lab06MockSkills @(
    "candidate-evidence-summary",
    "negative-news-risk-review",
    "watchlist-handoff",
    "simulation-portfolio-plan",
    "requires_human_confirmation"
)
Require-Contains "labs/06-skill-registry/src/skill_registry.py" $lab06SkillRegistry @(
    "SkillDefinition",
    "SkillRegistry",
    "list_skills",
    "get_skill",
    "mock_skills.json"
)
Require-Contains "labs/06-skill-registry/src/skill_selector.py" $lab06SkillSelector @(
    "build_selection_context",
    "select_skills",
    "matched_triggers",
    "disabled_reasons",
    "missing_risk_disclosure",
    "requires_human_confirmation"
)
Require-Contains "labs/06-skill-registry/src/run_lab.py" $lab06RunLab @(
    "run_skill_registry",
    "run_user_preference_memory",
    "registered_skills",
    "skill_selection_trace",
    "selected_skills",
    "disabled_skills",
    "Lab 07 Skill Generation",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/06-skill-registry/demo/run_demo.py" $lab06Demo @(
    "run_skill_registry",
    "--user-id",
    "--output",
    "selected_skills",
    "disabled_skills"
)
Require-Contains "labs/06-skill-registry/tests/test_skill_registry.py" $lab06SkillRegistryTests @(
    "test_registry_loads_four_mock_skills",
    "test_get_skill_finds_candidate_evidence_summary",
    "candidate-evidence-summary"
)
Require-Contains "labs/06-skill-registry/tests/test_skill_selector.py" $lab06SkillSelectorTests @(
    "test_normal_request_selects_summary_and_risk_review",
    "test_blocked_request_does_not_select_execution_skills",
    "test_missing_risk_disclosure_disables_handoff_and_simulation"
)
Require-Contains "labs/06-skill-registry/tests/test_run_lab.py" $lab06RunLabTests @(
    "test_normal_request_generates_selection_outputs",
    "test_blocked_request_does_not_select_execution_skills",
    "PROHIBITED_KEYS"
)

Require-Contains "labs/07-skill-generation/AGENTS.md" $lab07Agents @(
    "Skill Generation",
    "generated_skill_draft",
    "skill_draft_markdown",
    "draft_review",
    "risk_disclosure",
    "Lab 08 Finance Provider Adapter"
)
Require-Contains "labs/07-skill-generation/README.md" $lab07Readme @(
    "Skill Generation",
    ".agents/",
    ".codex/",
    "generated_skill_draft",
    "skill_draft_markdown",
    "draft_review",
    "needs_human_review",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1"
)
Require-Contains "labs/07-skill-generation/data/skill_draft_template.md" $lab07DraftTemplate @(
    "DRAFT",
    "Trigger Scenarios",
    "Disabled Scenarios",
    "Human Confirmation Points",
    "Safety Boundaries",
    "Test Cases"
)
Require-Contains "labs/07-skill-generation/src/skill_draft_builder.py" $lab07DraftBuilder @(
    "build_skill_draft",
    "choose_draft_source_skill",
    "generated_skill_draft",
    "skill_draft_markdown",
    "human_confirmation_points",
    "safety_boundaries",
    "risk_disclosure"
)
Require-Contains "labs/07-skill-generation/src/skill_safety_review.py" $lab07SafetyReview @(
    "review_skill_draft",
    "needs_human_review",
    "missing_risk_disclosure",
    "missing_disabled_scenarios",
    "missing_human_review_or_confirmation",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/07-skill-generation/src/run_lab.py" $lab07RunLab @(
    "run_skill_generation",
    "run_skill_registry",
    "generated_skill_draft",
    "skill_draft_markdown",
    "draft_review",
    "Lab 08 Finance Provider Adapter",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/07-skill-generation/demo/run_demo.py" $lab07Demo @(
    "run_skill_generation",
    "--user-id",
    "--output",
    "review_status"
)
Require-Contains "labs/07-skill-generation/tests/test_skill_draft_builder.py" $lab07DraftBuilderTests @(
    "test_builder_generates_required_draft_fields",
    "test_skill_draft_markdown_contains_draft_marker",
    "DRAFT"
)
Require-Contains "labs/07-skill-generation/tests/test_skill_safety_review.py" $lab07SafetyReviewTests @(
    "test_review_requires_human_review_for_valid_draft",
    "test_review_checks_disabled_scenarios_risk_disclosure_and_human_confirmation",
    "test_review_detects_prohibited_output_keys"
)
Require-Contains "labs/07-skill-generation/tests/test_run_lab.py" $lab07RunLabTests @(
    "test_normal_request_generates_draft_review",
    "test_blocked_request_does_not_generate_activatable_skill",
    "test_does_not_create_runtime_config_directories",
    "PROHIBITED_KEYS"
)

Require-Contains "labs/08-mx-skills-adapter/AGENTS.md" $lab08Agents @(
    "Finance Provider Adapter",
    "candidate-screen",
    "external-finance",
    "AdapterResult",
    "adapter_trace",
    "safety_gate",
    "real_provider_allowed",
    "raw_response_persisted",
    "risk_disclosure",
    "Lab 09 Research Planner DAG"
)
Require-Contains "labs/08-mx-skills-adapter/README.md" $lab08Readme @(
    "Adapter",
    ".agents/",
    ".codex",
    "mock-finance",
    "external-finance-stub",
    "external-finance",
    "candidate-screen",
    "market-data",
    "finance-news",
    "mx-skills",
    "https://dl.dfcfs.com/m/itc4",
    "--allow-real-provider",
    "FINANCE_PROVIDER_ALLOW_REAL",
    "manual_test_real_mx_adapter.py",
    "raw_response_persisted",
    "AdapterResult",
    "adapter_trace",
    "safety_gate",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1"
)
Require-Contains "labs/08-mx-skills-adapter/data/adapter_capabilities.json" $lab08Capabilities @(
    "mock-finance",
    "external-finance-stub",
    "external-finance",
    "candidate-screen",
    "market-data",
    "finance-news",
    "mx-skills",
    "https://dl.dfcfs.com/m/itc4",
    "requires_human_confirmation"
)
Require-Contains "labs/08-mx-skills-adapter/src/adapter_contract.py" $lab08Contract @(
    "AdapterCapability",
    "AdapterResult",
    "normalize_capability",
    "normalize_adapter_name",
    "mx-xuangu",
    "real-mx",
    "adapter_name",
    "provider_mode",
    "requires_api_key",
    "requires_human_confirmation",
    "network_request_sent",
    "api_key_present",
    "raw_response_persisted"
)
Require-Contains "labs/08-mx-skills-adapter/src/mock_mx_adapter.py" $lab08MockAdapter @(
    "MockFinanceAdapter",
    "select_candidates",
    "fetch_market_data",
    "search_finance_news",
    "candidate-screen",
    "market-data",
    "MockMXAdapter"
)
Require-Contains "labs/08-mx-skills-adapter/src/real_mx_adapter.py" $lab08RealAdapter @(
    "ExternalFinanceAdapter",
    "FINANCE_PROVIDER_ALLOW_REAL",
    "FINANCE_PROVIDER_API_KEY",
    "FINANCE_PROVIDER_BASE_URL",
    "MX_ALLOW_REAL_PROVIDER",
    "MX_APIKEY",
    "mx-skills",
    "https://dl.dfcfs.com/m/itc4",
    "allow_real_provider",
    "network_request_sent",
    "api_key_present",
    "raw_response_persisted",
    "transport"
)
Require-Contains "labs/08-mx-skills-adapter/src/real_mx_adapter_stub.py" $lab08RealStub @(
    "ExternalFinanceAdapterStub",
    "EXTERNAL_PROVIDER_DISABLED_REASON",
    "network_request_sent",
    "api_key_read",
    "blocked"
)
Require-Contains "labs/08-mx-skills-adapter/src/adapter_registry.py" $lab08Registry @(
    "AdapterRegistry",
    "list_adapters",
    "get_adapter",
    "call_adapter",
    "DEFAULT_ADAPTER_NAME",
    "external-finance"
)
Require-Contains "labs/08-mx-skills-adapter/src/run_lab.py" $lab08RunLab @(
    "run_finance_provider_adapter",
    "run_skill_generation",
    "registered_adapters",
    "adapter_trace",
    "safety_gate",
    "real_provider_allowed",
    "real_provider_attempted",
    "allow_real_provider",
    "FINANCE_PROVIDER_ALLOW_REAL",
    "Lab 09 Research Planner DAG",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/08-mx-skills-adapter/demo/run_demo.py" $lab08Demo @(
    "run_finance_provider_adapter",
    "--adapter-mode",
    "--allow-real-provider",
    "--output",
    "real_provider_allowed"
)
Require-Contains "labs/08-mx-skills-adapter/tests/test_adapter_contract.py" $lab08ContractTests @(
    "test_adapter_result_has_required_fields",
    "test_registry_lists_mock_real_stub_and_real_provider",
    "validate_adapter_result"
)
Require-Contains "labs/08-mx-skills-adapter/tests/test_mock_mx_adapter.py" $lab08MockAdapterTests @(
    "test_mock_adapter_calls_candidate_screen",
    "test_mock_adapter_calls_market_data_and_finance_news",
    "test_mock_adapter_accepts_legacy_mx_aliases"
)
Require-Contains "labs/08-mx-skills-adapter/tests/test_real_mx_adapter.py" $lab08RealAdapterTests @(
    "test_real_adapter_missing_key_is_blocked_without_network",
    "test_real_adapter_missing_cli_allow_is_blocked_without_reading_key",
    "test_real_adapter_success_path_uses_fake_transport",
    "fake_transport",
    "raw_response_persisted"
)
Require-Contains "labs/08-mx-skills-adapter/tests/test_real_mx_adapter_stub.py" $lab08RealStubTests @(
    "test_external_adapter_stub_is_blocked_without_network_or_key",
    "network_request_sent",
    "api_key_read"
)
Require-Contains "labs/08-mx-skills-adapter/tests/test_run_lab.py" $lab08RunLabTests @(
    "test_normal_request_generates_adapter_trace",
    "test_blocked_request_does_not_call_adapter",
    "test_real_stub_mode_is_blocked_by_safety_gate",
    "test_real_adapter_missing_allow_flag_is_blocked_without_network",
    "test_real_adapter_can_use_fake_transport_success_path",
    "test_does_not_create_runtime_config_directories",
    "PROHIBITED_KEYS"
)
Require-Contains "labs/08-mx-skills-adapter/tests/manual_test_real_mx_adapter.py" $lab08ManualRealAdapterTest @(
    "RUN_REAL_FINANCE_INTEGRATION",
    "FINANCE_PROVIDER_ALLOW_REAL",
    "FINANCE_PROVIDER_API_KEY",
    "RUN_REAL_MX_INTEGRATION",
    "MX_ALLOW_REAL_PROVIDER",
    "MX_APIKEY",
    "raw_response_persisted"
)

Require-Contains "labs/09-research-planner/AGENTS.md" $lab09Agents @(
    "Research Planner DAG",
    "planner_trace",
    "human_review_gate",
    "waiting_human_confirmation",
    "risk_disclosure"
)
Require-Contains "labs/09-research-planner/README.md" $lab09Readme @(
    "Research Planner DAG",
    "planner_trace",
    "research_dag",
    "blocked_nodes",
    "skipped_nodes",
    "waiting_human_confirmation",
    "risk_disclosure",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1",
    "Lab 10 Evidence Report"
)
Require-Contains "labs/09-research-planner/data/planner_template.json" $lab09PlannerTemplate @(
    "parse_and_route",
    "adapter_capability_check",
    "candidate_generation",
    "market_data_check",
    "news_risk_check",
    "evidence_context_attach",
    "memory_preference_adjustment",
    "skill_selection",
    "human_review_gate",
    "failure_behavior"
)
Require-Contains "labs/09-research-planner/src/dag_model.py" $lab09DagModel @(
    "ResearchDagNode",
    "VALID_STATUSES",
    "validate_dag_dependencies",
    "topological_sort_nodes",
    "get_dependency_statuses"
)
Require-Contains "labs/09-research-planner/src/planner_builder.py" $lab09PlannerBuilder @(
    "build_research_dag",
    "REQUIRED_NODE_IDS",
    "planner_template.json",
    "safety_gate",
    "risk_disclosure_present"
)
Require-Contains "labs/09-research-planner/src/planner_executor.py" $lab09PlannerExecutor @(
    "execute_research_planner",
    "planner_trace",
    "waiting_human_confirmation",
    "human_review_gate",
    "PROHIBITED_OUTPUT_KEYS",
    "contains_prohibited_output_key"
)
Require-Contains "labs/09-research-planner/src/run_lab.py" $lab09RunLab @(
    "run_research_planner_dag",
    "run_finance_provider_adapter",
    "research_dag",
    "planner_trace",
    "Lab 10 Evidence Report",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/09-research-planner/demo/run_demo.py" $lab09Demo @(
    "run_research_planner_dag",
    "--adapter-mode",
    "planner_trace_count",
    "waiting_human_confirmation_nodes"
)
Require-Contains "labs/09-research-planner/tests/test_dag_model.py" $lab09DagModelTests @(
    "test_validate_dag_dependencies_accepts_valid_dag",
    "test_validate_dag_dependencies_rejects_missing_dependency",
    "test_validate_dag_dependencies_rejects_cycle"
)
Require-Contains "labs/09-research-planner/tests/test_planner_builder.py" $lab09PlannerBuilderTests @(
    "test_builder_generates_all_required_nodes",
    "test_builder_injects_adapter_context"
)
Require-Contains "labs/09-research-planner/tests/test_planner_executor.py" $lab09PlannerExecutorTests @(
    "test_normal_mock_path_waits_for_human_confirmation",
    "test_upstream_blocked_skips_downstream_nodes",
    "test_missing_risk_disclosure_blocks_human_review_gate",
    "test_planner_trace_contains_each_node_status_and_reason"
)
Require-Contains "labs/09-research-planner/tests/test_run_lab.py" $lab09RunLabTests @(
    "test_run_lab_normal_request_waits_for_human_confirmation",
    "test_run_lab_blocked_request_propagates_to_dag",
    "PROHIBITED_KEYS"
)

Require-Contains "labs/10-evidence-report/AGENTS.md" $lab10Agents @(
    "Evidence Report",
    "report_generation_trace",
    "evidence_refs",
    "human_review_required",
    "risk_disclosure"
)
Require-Contains "labs/10-evidence-report/README.md" $lab10Readme @(
    "Evidence Report",
    "evidence_report",
    "report_generation_trace",
    "evidence_refs",
    "risk_disclosure",
    "human_review_required",
    "run-lab-demo.ps1",
    "run-lab-tests.ps1",
    "Lab 11 Simulation Portfolio"
)
Require-Contains "labs/10-evidence-report/data/report_template.json" $lab10Template @(
    "report_header",
    "strategy_summary",
    "planner_summary",
    "candidate_observation_pool",
    "evidence_table",
    "retrieved_context_table",
    "risk_and_limitations",
    "human_review_checklist",
    "next_steps"
)
Require-Contains "labs/10-evidence-report/src/report_model.py" $lab10ReportModel @(
    "EvidenceReference",
    "ReportSection",
    "PROHIBITED_OUTPUT_KEYS",
    "find_prohibited_output_key_paths",
    "find_prohibited_semantic_paths",
    "sanitize_text"
)
Require-Contains "labs/10-evidence-report/src/evidence_collector.py" $lab10EvidenceCollector @(
    "collect_report_inputs",
    "build_evidence_references",
    "build_candidate_observations",
    "build_evidence_gaps",
    "candidate_evidence",
    "retrieved_context",
    "planner_trace"
)
Require-Contains "labs/10-evidence-report/src/report_builder.py" $lab10ReportBuilder @(
    "build_report_from_planner",
    "build_report_generation_trace",
    "evidence_report",
    "report_generation_trace",
    "human_review_required",
    "Lab 11 Simulation Portfolio"
)
Require-Contains "labs/10-evidence-report/src/report_safety.py" $lab10ReportSafety @(
    "review_report_output",
    "missing_risk_disclosure",
    "missing_human_review_required",
    "prohibited_output_key",
    "prohibited_semantic_text"
)
Require-Contains "labs/10-evidence-report/src/run_lab.py" $lab10RunLab @(
    "run_evidence_report",
    "run_research_planner_dag",
    "summarize_planner_output",
    "evidence_report",
    "report_generation_trace",
    "report_safety_review",
    "Lab 11 Simulation Portfolio",
    "PROHIBITED_OUTPUT_KEYS"
)
Require-Contains "labs/10-evidence-report/demo/run_demo.py" $lab10Demo @(
    "run_evidence_report",
    "--adapter-mode",
    "report_generation_trace_count",
    "evidence_ref_count"
)
Require-Contains "labs/10-evidence-report/tests/test_report_model.py" $lab10ReportModelTests @(
    "test_evidence_reference_serializes_required_fields",
    "test_detects_prohibited_output_keys",
    "test_sanitize_text_redacts_prohibited_semantics"
)
Require-Contains "labs/10-evidence-report/tests/test_evidence_collector.py" $lab10EvidenceCollectorTests @(
    "test_collects_candidate_context_adapter_and_planner_refs",
    "test_candidate_observations_keep_evidence_refs"
)
Require-Contains "labs/10-evidence-report/tests/test_report_builder.py" $lab10ReportBuilderTests @(
    "test_builds_report_with_all_core_sections",
    "test_generation_trace_covers_each_section",
    "test_blocked_planner_creates_blocked_report_and_gaps"
)
Require-Contains "labs/10-evidence-report/tests/test_report_safety.py" $lab10ReportSafetyTests @(
    "test_review_passes_valid_report",
    "test_review_detects_missing_risk_disclosure",
    "test_review_detects_prohibited_output_keys",
    "test_review_detects_prohibited_semantics"
)
Require-Contains "labs/10-evidence-report/tests/test_run_lab.py" $lab10RunLabTests @(
    "test_normal_request_generates_reviewable_report",
    "test_blocked_request_generates_blocked_report_with_gaps",
    "test_report_generation_trace_covers_core_sections",
    "test_does_not_create_runtime_config_directories",
    "PROHIBITED_KEYS"
)

Require-Contains "labs/shared/testing/README.md" $sharedTestingReadme @("run_lab_tests.py")
Require-Contains "labs/shared/testing/run_lab_tests.py" $sharedTestingRunner @("unittest", "--lab", "report_builder", "report_safety")
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

$dynamicLabDirs = Get-ChildItem -LiteralPath (Join-Path $root "labs") -Directory |
    Where-Object { $_.Name -match '^\d{2}-' } |
    Sort-Object Name

$requiredLabFiles = @(
    "AGENTS.md",
    "README.md",
    "demo/run_demo.py",
    "outputs/.gitkeep"
)

$labNavigationDocs = @(
    @{ Name = "README.md"; Content = $readme },
    @{ Name = "labs/README.md"; Content = $labsReadme },
    @{ Name = "docs/start-here.md"; Content = $startHere },
    @{ Name = "docs/product/README.md"; Content = $productReadme },
    @{ Name = "docs/product/lab-plan.md"; Content = $labPlan },
    @{ Name = "docs/product/showcase-framework.md"; Content = $showcaseFramework },
    @{ Name = "docs/document-graph.md"; Content = $documentGraph },
    @{ Name = "roadmap.md"; Content = $roadmap }
)

foreach ($labDir in $dynamicLabDirs) {
    $labFolder = $labDir.Name
    $labNumber = $labFolder.Substring(0, 2)

    foreach ($relativeFile in $requiredLabFiles) {
        $requiredPath = Join-Path $labDir.FullName $relativeFile
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            Add-Failure "Lab $labFolder missing required file: $relativeFile"
        }
    }

    $testsPath = Join-Path $labDir.FullName "tests"
    if (-not (Test-Path -LiteralPath $testsPath -PathType Container)) {
        Add-Failure "Lab $labFolder missing required directory: tests/"
    }

    foreach ($navDoc in $labNavigationDocs) {
        if (-not (Test-TextHasLabReference $navDoc["Content"] $labFolder $labNumber)) {
            Add-Failure "$($navDoc["Name"]) missing navigation reference for Lab $labNumber ($labFolder)"
        }
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Output $_ }
    throw "Related docs audit failed."
}

Write-Output "Related docs audit passed."
