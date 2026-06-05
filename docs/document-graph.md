# Document Graph

这个文档用图的方式整理 `Learning_Agent` 仓库的内容结构、来源路线和后续维护关系。

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

    S1 --> D01["01 Workflow vs Agent"]
    S1 --> D02["02 Agent Loop"]
    S1 --> D03["03 Tool Use"]

    S2 --> D04["04 RAG"]
    S2 --> D05["05 Memory"]
    S2 --> D06["06 MCP"]

    S3 --> D07["07 Agent Harness"]
    S3 --> D08["08 Coding Agent"]
    S3 --> D09["09 Subagent / Multi-Agent"]
    S3 --> D10["10 Skills"]
    S3 --> D11["11 Browser / Computer Use Agent"]
    S3 --> D12["12 Evaluation / Trace / Safety"]

    X7 --> P0["投研系统愿景"]
    X7 --> P1["Lab 总计划"]
    X7 --> P2["密钥、安全与合规边界"]
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

    D01 --> P1["patterns/workflow-vs-agent"]
    D07 --> E1["engineering/permission-boundary"]
    D08 --> L1["labs/coding-agent"]
    D10 --> S1["skills/agent-article-writing"]
    D12 --> E2["engineering/evaluation-checklist"]

    D01 --> PR1["product/投研系统愿景"]
    D02 --> L02["labs/02-strategy-agent-loop"]
    D03 --> L03["labs/03-finance-tool-use-mock"]
    D04 --> L04["labs/04-research-rag-basic"]
    D05 --> L05["labs/05-user-preference-memory"]
    D06 --> L08["labs/08-mx-skills-adapter"]
    D07 --> L09["labs/09-research-planner"]
    D10 --> L07["labs/07-skill-generation"]
    D12 --> L12["labs/12-evaluation-safety"]
```

## 仓库维护关系

```mermaid
flowchart TD
    A["新增或重写文章"] --> B["hooks/content-update.md"]
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
| 资料精读 | [readings/](readings/) | 拆解官方文档、论文、工程博客和开源项目。 |
| 设计模式 | [patterns/](patterns/) | 沉淀可复用 Agent 模式和适用边界。 |
| 工程清单 | [engineering/](engineering/) | 管理权限、Trace、Eval、安全、成本等上线检查项。 |
| 产品设计 | [product/](product/) | 定义个性化投研 Agent 系统愿景、Lab 总计划、密钥安全和财经输出边界。 |
| 实践实验 | [../labs/](../labs/) | 承接基础文章，补最小可运行实验。 |
| Skill 示例 | [../skills/](../skills/) | 把重复流程沉淀成 `SKILL.md` 示例。 |
| 待办机制 | [../TODO.md](../TODO.md) | 维护当前阶段任务、优先级、产出和验收标准。 |

## 产品主线映射

| 文档 | 作用 |
| --- | --- |
| [product/personalized-investment-research-agent.md](product/personalized-investment-research-agent.md) | 定义个性化投研 Agent 系统愿景、边界、架构和 Skill 固化思路。 |
| [product/lab-plan.md](product/lab-plan.md) | 把 12 篇基础文章映射成 12 个投研 Labs。 |
| [product/security-and-secrets.md](product/security-and-secrets.md) | 定义 Hermes 注入密钥、`.env.example`、提交前检查和财经输出边界。 |
| [../labs/README.md](../labs/README.md) | Labs 入口，说明投研主线和统一要求。 |
| [../labs/01-strategy-intake/README.md](../labs/01-strategy-intake/README.md) | 第一个可运行 Lab，把自然语言投研策略解析成 `StrategySpec`。 |
| [../labs/shared/investment_research_case/README.md](../labs/shared/investment_research_case/README.md) | 共享案例材料结构。 |
| [../labs/shared/testing/README.md](../labs/shared/testing/README.md) | 统一 Lab 测试入口说明。 |
| [../scripts/run-lab-demo.ps1](../scripts/run-lab-demo.ps1) | 统一 demo 运行封装。 |
| [../scripts/run-lab-web.ps1](../scripts/run-lab-web.ps1) | 统一本地 web demo 运行封装。 |
| [../scripts/run-lab-tests.ps1](../scripts/run-lab-tests.ps1) | 统一 Lab 回归测试封装。 |
