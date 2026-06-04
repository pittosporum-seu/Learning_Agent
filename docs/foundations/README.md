# Agent 基础知识

这一组文章用于建立 Agent 学习的底层概念框架。

推荐阅读顺序：

| 顺序 | 主题 | 文件 |
| --- | --- | --- |
| 01 | Workflow vs Agent | [01-workflow-vs-agent.md](01-workflow-vs-agent.md) |
| 02 | Agent Loop | [02-agent-loop.md](02-agent-loop.md) |
| 03 | Tool Use | [03-tool-use.md](03-tool-use.md) |
| 04 | RAG | [04-rag.md](04-rag.md) |
| 05 | Memory | [05-memory.md](05-memory.md) |
| 06 | MCP | [06-mcp.md](06-mcp.md) |
| 07 | Agent Harness | [07-agent-harness.md](07-agent-harness.md) |
| 08 | Coding Agent | [08-coding-agent.md](08-coding-agent.md) |
| 09 | Subagent / Multi-Agent | [09-subagent-multi-agent.md](09-subagent-multi-agent.md) |
| 10 | Skills | [10-skills.md](10-skills.md) |

核心脉络：

```text
先判断是否需要 Agent
  -> 理解 Agent Loop
  -> 给 Agent 接入工具
  -> 用 RAG 补足知识
  -> 用 Memory 管理上下文和经验
  -> 用 MCP 统一工具和数据源
  -> 用 Harness 提升可靠性
  -> 在 Coding Agent 场景里理解真实工程闭环
  -> 用 Subagent / Multi-Agent 管理复杂任务的上下文和分工
  -> 用 Skills 把重复流程沉淀成可复用能力包
```
