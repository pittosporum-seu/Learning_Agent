# Learning Agent

这个仓库用来系统整理 Agent 学习笔记、核心概念、实践实验和参考资料。

目标不是一上来堆框架，而是把 Agent 学习拆成几件能长期沉淀的事：

- 分清什么时候该用 Workflow，什么时候才需要 Agent。
- 理解 Agent Loop、Tool Use、RAG、Memory、MCP、Harness、Coding Agent、Subagent 这些基础模块。
- 逐步补充可运行实验，而不是只停留在概念解释。
- 沉淀可复用的阅读笔记、案例分析和工程清单。

## 学习路线

整体写作规划见：[Agent 基础知识系列规划](docs/series-plan.md)。

### Stage 1: Agent 基础知识

| 序号 | 主题 | 笔记 |
| --- | --- | --- |
| 01 | Workflow vs Agent | [不要一上来就造 Agent，先分清 Workflow 和 Agent](docs/foundations/01-workflow-vs-agent.md) |
| 02 | Agent Loop | [模型是怎么“边看边干活”的](docs/foundations/02-agent-loop.md) |
| 03 | Tool Use | [工具不是插件，而是 Agent 的手脚](docs/foundations/03-tool-use.md) |
| 04 | RAG | [让 Agent 基于资料回答，而不是靠感觉](docs/foundations/04-rag.md) |
| 05 | Memory | [短期上下文、长期记忆和反思机制](docs/foundations/05-memory.md) |
| 06 | MCP | [Agent 的 USB-C，工具和数据源的统一接口](docs/foundations/06-mcp.md) |
| 07 | Agent Harness | [真正让 Agent 可靠的不是模型，是工程底座](docs/foundations/07-agent-harness.md) |
| 08 | Coding Agent | [为什么代码库是 Agent 最好的训练场](docs/foundations/08-coding-agent.md) |
| 09 | Subagent / Multi-Agent | [多 Agent 不是聊天群，而是上下文隔离和任务分工](docs/foundations/09-subagent-multi-agent.md) |

### Stage 2: 经典资料精读

后续会把论文、官方文档、工程博客拆成结构化阅读笔记，重点记录：

- 这篇资料解决什么问题。
- 它适合 Agent 系统里的哪个模块。
- 对真实工程有什么启发。
- 有哪些限制和容易误用的地方。

### Stage 3: 最小可运行实验

后续在 `labs/` 里补充小实验，例如：

- 最小 Agent Loop。
- 函数调用与工具路由。
- RAG 检索与引用。
- 简单 Memory 机制。
- MCP Server / Client 示例。
- Agent 评测与回归测试。

### Stage 4: Agent 工程化

后续重点沉淀：

- 权限控制。
- 工具边界。
- 上下文管理。
- 运行日志。
- 评测体系。
- 成本与延迟优化。
- 人机协同工作流。

## 仓库结构

```text
.
├── README.md
├── roadmap.md
├── docs/
│   ├── README.md
│   ├── series-plan.md
│   └── foundations/
│       ├── 01-workflow-vs-agent.md
│       ├── 02-agent-loop.md
│       ├── 03-tool-use.md
│       ├── 04-rag.md
│       ├── 05-memory.md
│       ├── 06-mcp.md
│       ├── 07-agent-harness.md
│       ├── 08-coding-agent.md
│       └── 09-subagent-multi-agent.md
├── labs/
│   └── README.md
└── resources/
    └── README.md
```

## 维护原则

- 每篇笔记尽量回答一个明确问题。
- 概念解释和工程实践分开沉淀。
- 先用最小例子讲清楚，再扩展复杂系统。
- 所有实验尽量可运行、可复现、可测试。
- 避免把 Agent 神秘化，优先讨论边界、成本和可靠性。

## 推荐阅读

- Anthropic: Building Effective Agents
- Model Context Protocol documentation
- OpenAI Agents SDK documentation
- LangGraph documentation
- LlamaIndex documentation
