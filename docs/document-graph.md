# Document Graph

这个文档用图的方式整理 `Learning_Agent` 仓库的内容结构、来源路线和维护关系。

## 来源路线

这套 `Agent基础知识` 系列最初围绕 [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub) 的学习路线展开，再结合 Anthropic、OpenAI、Claude Code、MCP、SWE-bench、WebArena 等资料补充扩展。

```mermaid
flowchart TD
    A["datawhalechina/Agent-Learning-Hub"] --> B["Agent基础知识系列"]

    C["Anthropic / Building Effective Agents"] --> B
    D["OpenAI Agents / Evals / Computer Use"] --> B
    E["Claude Code / Skills / Subagents"] --> B
    F["MCP / Tool Ecosystem"] --> B
    G["SWE-bench / WebArena / AgentBench"] --> B

    B --> S1["第一组：基础概念"]
    B --> S2["第二组：知识与能力扩展"]
    B --> S3["第三组：工程落地"]
    B --> X1["资料精读 readings"]
    B --> X2["设计模式 patterns"]
    B --> X3["工程清单 engineering"]
    B --> X4["Skills 示例"]
    B --> X5["Labs 实验"]
    B --> X6["TODO.md 待办板"]
    B --> X7["Product Design 个性化投研 Agent"]
    B --> X8["Start Here 学习入口"]
    B --> X9["Glossary 术语表"]

    X8 --> X5
    X8 --> X7
    X7 --> P0["投研系统愿景"]
    X7 --> P1["Lab 总计划"]
    X7 --> P2["密钥、安全与合规边界"]
    X7 --> P3["Agent 学习展示框架"]
    X7 --> P4["Lab 09 Planner DAG 设计"]
    X7 --> X5
```

## 文章依赖关系

```mermaid
flowchart LR
    D01["01 Workflow vs Agent"] --> D02["02 Agent Loop"]
    D02 --> D03["03 Tool Use"]
    D03 --> D04["04 RAG"]
    D04 --> D05["05 Memory"]
    D05 --> D06["06 MCP"]
    D06 --> D07["07 Agent Harness"]
    D07 --> D08["08 Coding Agent"]
    D07 --> D09["09 Subagent / Multi-Agent"]
    D07 --> D10["10 Skills"]
    D07 --> D11["11 Browser / Computer Use Agent"]
    D08 --> D12["12 Evaluation / Trace / Safety"]
    D09 --> D12
    D10 --> D12
    D11 --> D12

    D01 --> L01["labs/01-strategy-intake"]
    D02 --> L02["labs/02-strategy-agent-loop"]
    D03 --> L03["labs/03-finance-tool-use-mock"]
    D04 --> L04["labs/04-research-rag-basic"]
    D05 --> L05["labs/05-user-preference-memory"]
    D06 --> L08["labs/08-mx-skills-adapter"]
    D07 --> L09["labs/09-research-planner"]
    D10 --> L06["labs/06-skill-registry"]
    D10 --> L07["labs/07-skill-generation"]
    D12 --> L12["labs/12-evaluation-safety"]
```

## 投研 Lab 主线

```mermaid
flowchart TD
    U["自然语言策略"] --> L01["Lab 01 Strategy Intake Router"]
    L01 --> R0["routing_decision"]
    R0 --> R1["规则基线 StrategySpec"]
    L01 --> M1["可配置模型解析 StrategySpec"]
    R1 --> L02["Lab 02 Agent Loop"]
    M1 --> L02
    L02 --> P["mock 投研计划"]
    P --> L03["Lab 03 Finance Tool Use Mock"]
    L03 --> L04["Lab 04 Research RAG Basic"]
    L04 --> L05["Lab 05 User Preference Memory"]
    L05 --> L06["Lab 06 Skill Registry"]
    L06 --> L07["Lab 07 Skill Generation"]
    L07 --> L08["Lab 08 Finance Provider Adapter"]
    L08 --> L09["Lab 09 Research Planner"]
    L09 --> L10["Lab 10 Evidence Report"]
    L10 --> L11["Lab 11 Simulation Portfolio"]
    L11 --> L12["Lab 12 Evaluation & Safety"]
```

## 仓库维护关系

```mermaid
flowchart TD
    A["新增或重写文章 / Product / Labs / Skills 文档"] --> B["hooks/content-update.md"]
    T["新增或完成待办"] --> B
    B --> C["同步 README.md"]
    B --> D["同步 docs/foundations/README.md"]
    B --> E["同步 docs/series-plan.md"]
    B --> F["同步 roadmap.md"]
    B --> G["同步 docs/document-graph.md"]
    B --> H["同步 resources/README.md"]
    B --> O["同步 docs/readings / patterns / engineering / skills"]
    B --> P["同步 TODO.md"]
    B --> Q["同步 docs/product 和 labs"]

    B --> I["scripts/check-content.ps1"]
    B --> R["scripts/check-secrets.ps1"]
    B --> J["scripts/audit-related-docs.ps1"]
    B --> U["scripts/run-lab-tests.ps1"]

    I --> K["清理过程性内容和跟踪参数"]
    R --> S["检查真实密钥和凭据是否泄露"]
    J --> L["审核相关文档是否同步"]
    U --> V["运行 Lab 回归测试"]

    K --> M["git diff review"]
    S --> M
    L --> M
    V --> M
    M --> N["commit / push"]
```

## 文章文件映射

| 序号 | 主题 | 文件 |
| --- | --- | --- |
| 01 | Workflow vs Agent | [01-workflow-vs-agent.md](foundations/01-workflow-vs-agent.md) |
| 02 | Agent Loop | [02-agent-loop.md](foundations/02-agent-loop.md) |
| 03 | Tool Use | [03-tool-use.md](foundations/03-tool-use.md) |
| 04 | RAG | [04-rag.md](foundations/04-rag.md) |
| 05 | Memory | [05-memory.md](foundations/05-memory.md) |
| 06 | MCP | [06-mcp.md](foundations/06-mcp.md) |
| 07 | Agent Harness | [07-agent-harness.md](foundations/07-agent-harness.md) |
| 08 | Coding Agent | [08-coding-agent.md](foundations/08-coding-agent.md) |
| 09 | Subagent / Multi-Agent | [09-subagent-multi-agent.md](foundations/09-subagent-multi-agent.md) |
| 10 | Skills | [10-skills.md](foundations/10-skills.md) |
| 11 | Browser / Computer Use Agent | [11-browser-computer-use-agent.md](foundations/11-browser-computer-use-agent.md) |
| 12 | Evaluation / Trace / Safety | [12-evaluation-trace-safety.md](foundations/12-evaluation-trace-safety.md) |

## 扩展层映射

| 层级 | 目录 | 作用 |
| --- | --- | --- |
| 学习入口 | [start-here.md](start-here.md) | 给第一次进入仓库的人三条学习路径和可运行命令。 |
| 术语表 | [glossary.md](glossary.md) | 统一 Agent、Workflow、RAG、Memory、Trace、Guardrails 等核心术语。 |
| 资料精读 | [readings/](readings/) | 拆解官方文档、论文、工程博客和开源项目。 |
| 设计模式 | [patterns/](patterns/) | 沉淀可复用 Agent 模式和适用边界。 |
| 工程清单 | [engineering/](engineering/) | 管理权限、trace、eval、安全、成本等上线检查项。 |
| 产品设计 | [product/](product/) | 定义个性化投研 Agent 系统愿景、展示框架、Lab 总计划、密钥安全和财经输出边界。 |
| 实践实验 | [../labs/](../labs/) | 承接基础文章，补最小可运行实验。 |
| Skill 示例 | [../skills/](../skills/) | 把重复流程沉淀成 `SKILL.md` 示例。 |
| 仓库规则 | [../AGENTS.md](../AGENTS.md) | 为后续修改 Product、Labs、Skills 和文档结构提供持久规则。 |
| 维护模板 | [maintenance/codex-skill-templates/](maintenance/codex-skill-templates/README.md) | 保留 Lab 实现和文档同步的 Skill 模板资料，不是本地运行配置。 |
| 待办机制 | [../TODO.md](../TODO.md) | 维护当前阶段任务、优先级、产出和验收标准。 |

## 产品主线映射

| 文档 | 作用 |
| --- | --- |
| [product/README.md](product/README.md) | 个性化投研 Agent 产品案例入口，说明投研只是贯穿案例，并给出阅读顺序和财经输出边界。 |
| [product/personalized-investment-research-agent.md](product/personalized-investment-research-agent.md) | 定义个性化投研 Agent 系统愿景、边界、架构和 Skill 固化思路。 |
| [product/showcase-framework.md](product/showcase-framework.md) | 固化 Learning_Agent 的可运行展示框架，说明 Parts 0-12、统一数据契约、展示原则和实现顺序。 |
| [product/lab-plan.md](product/lab-plan.md) | 把 12 篇基础文章映射成 12 个投研 Labs。 |
| [product/lab09-research-planner-dag-design.md](product/lab09-research-planner-dag-design.md) | Lab 09 Research Planner DAG 设计文档，定义 DAG 节点、依赖、状态流转、失败传播、人工确认边界和后续实现结构。 |
| [product/security-and-secrets.md](product/security-and-secrets.md) | 定义 Hermes 注入密钥、`.env.example`、提交前检查和财经输出边界。 |
| [product/AGENTS.md](product/AGENTS.md) | 产品文档修改规则，约束产品定位、Lab 计划同步和财经输出边界。 |
| [../labs/README.md](../labs/README.md) | Labs 入口，说明投研主线和统一要求。 |
| [../labs/AGENTS.md](../labs/AGENTS.md) | Labs 修改规则，要求 mock-first、demo、tests 和可观察输出。 |
| [../labs/01-strategy-intake/README.md](../labs/01-strategy-intake/README.md) | 第一个可运行 Lab，把自然语言投研策略解析成 `StrategySpec` 和 `routing_decision`，支持规则基线和可配置模型解析模式。 |
| [../labs/01-strategy-intake/AGENTS.md](../labs/01-strategy-intake/AGENTS.md) | Lab 01 持久规则，约束 `StrategySpec`、`routing_decision` 和四类样例。 |
| [../labs/02-strategy-agent-loop/README.md](../labs/02-strategy-agent-loop/README.md) | 第二个可运行 Lab，把 `StrategySpec` 放进最小 Agent Loop，并用 structured trace 展示 observation、decision、why_this_action、result、guardrail 和 next_action_hint。 |
| [../labs/02-strategy-agent-loop/AGENTS.md](../labs/02-strategy-agent-loop/AGENTS.md) | Lab 02 持久规则，约束 Agent Loop 和 structured trace。 |
| [../labs/03-finance-tool-use-mock/README.md](../labs/03-finance-tool-use-mock/README.md) | 第三个可运行 Lab，用 mock 工具展示 Tool Use、`tool_trace` 和 `candidate_evidence`。 |
| [../labs/03-finance-tool-use-mock/AGENTS.md](../labs/03-finance-tool-use-mock/AGENTS.md) | Lab 03 持久规则，约束 mock finance tools、证据化输出和禁止真实荐股。 |
| [../labs/04-research-rag-basic/README.md](../labs/04-research-rag-basic/README.md) | 第四个可运行 Lab，用本地 markdown 知识库展示 RAG、`retrieval_trace`、`retrieved_context` 和 `augmented_evidence`。 |
| [../labs/04-research-rag-basic/AGENTS.md](../labs/04-research-rag-basic/AGENTS.md) | Lab 04 持久规则，约束本地 mock RAG、来源字段和禁止真实投资建议。 |
| [../labs/05-user-preference-memory/README.md](../labs/05-user-preference-memory/README.md) | 第五个可运行 Lab，用本地 mock 用户偏好展示 Memory、`memory_trace` 和 `preference_adjusted_evidence`。 |
| [../labs/05-user-preference-memory/AGENTS.md](../labs/05-user-preference-memory/AGENTS.md) | Lab 05 持久规则，约束 mock Memory、证据视图调整和禁止覆盖安全边界。 |
| [../labs/06-skill-registry/README.md](../labs/06-skill-registry/README.md) | 第六个可运行 Lab，用本地 mock Skill 元数据展示 Skill Registry、`skill_selection_trace`、`selected_skills` 和 `disabled_skills`。 |
| [../labs/06-skill-registry/AGENTS.md](../labs/06-skill-registry/AGENTS.md) | Lab 06 持久规则，约束 mock Skill Registry、禁用场景、人工确认边界和禁止真实 runtime 配置。 |
| [../labs/07-skill-generation/README.md](../labs/07-skill-generation/README.md) | 第七个可运行 Lab，从 Lab 06 输出生成可审查 Skill draft、`skill_draft_markdown` 和 `draft_review`。 |
| [../labs/07-skill-generation/AGENTS.md](../labs/07-skill-generation/AGENTS.md) | Lab 07 持久规则，约束 Skill draft 生成、人工 review、禁止自动启用和禁止写 runtime 配置。 |
| [../labs/08-mx-skills-adapter/README.md](../labs/08-mx-skills-adapter/README.md) | 第八个可运行 Lab，用 mock-first adapter contract 展示 Finance Provider Adapter、`adapter_trace`、`safety_gate` 和 optional external provider manual integration。 |
| [../labs/08-mx-skills-adapter/AGENTS.md](../labs/08-mx-skills-adapter/AGENTS.md) | Lab 08 持久规则，约束 mock adapter、external provider stub、optional external provider、安全门和禁止真实 API 自动启用。 |
| [../labs/08-mx-skills-adapter/src/real_mx_adapter.py](../labs/08-mx-skills-adapter/src/real_mx_adapter.py) | Lab 08 可选真实 provider adapter，只有环境变量和显式命令行允许同时满足时才发送请求，并且不持久化 raw response。 |
| [../labs/08-mx-skills-adapter/tests/manual_test_real_mx_adapter.py](../labs/08-mx-skills-adapter/tests/manual_test_real_mx_adapter.py) | Lab 08 手动真实 provider integration test，默认跳过，只在本地显式环境闸门满足时运行。 |
| [../labs/shared/investment_research_case/README.md](../labs/shared/investment_research_case/README.md) | 共享案例材料结构。 |
| [../labs/shared/testing/README.md](../labs/shared/testing/README.md) | 统一 Lab 测试入口说明。 |
| [../scripts/run-lab-demo.ps1](../scripts/run-lab-demo.ps1) | 统一 demo 运行封装。 |
| [../scripts/run-lab-web.ps1](../scripts/run-lab-web.ps1) | 统一本地 web demo 运行封装。 |
| [../scripts/run-lab-tests.ps1](../scripts/run-lab-tests.ps1) | 统一 Lab 回归测试封装。 |
