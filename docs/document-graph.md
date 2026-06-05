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
```

## 仓库维护关系

```mermaid
flowchart TD
    A["新增或重写文章"] --> B["hooks/content-update.md"]
    B --> C["同步 README.md"]
    B --> D["同步 docs/foundations/README.md"]
    B --> E["同步 docs/series-plan.md"]
    B --> F["同步 roadmap.md"]
    B --> G["同步 docs/document-graph.md"]
    B --> H["同步 resources/README.md"]

    B --> I["scripts/check-content.ps1"]
    B --> J["scripts/audit-related-docs.ps1"]

    I --> K["清理过程性内容和跟踪参数"]
    J --> L["审核相关文档是否同步"]

    K --> M["git diff review"]
    L --> M
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

