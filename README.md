# Learning Agent

这个仓库用来系统整理 Agent 学习笔记、核心概念、实践实验和参考资料。

第一次进入仓库，建议先看：[Start Here](docs/start-here.md)。

目标不是一上来堆框架，而是把 Agent 学习拆成几件能长期沉淀的事：

- 分清什么时候该用 Workflow，什么时候才需要 Agent。
- 理解 Agent Loop、Tool Use、RAG、Memory、MCP、Harness、Coding Agent、Subagent、Skills、Browser / Computer Use Agent、Evaluation / Trace / Safety 这些基础模块。
- 逐步补充可运行实验，而不是只停留在概念解释。
- 沉淀可复用的阅读笔记、案例分析和工程清单。

## 学习路线

这套 `Agent基础知识` 系列最初围绕 [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub) 的学习路线展开，再结合 Anthropic、OpenAI、Claude Code、MCP、SWE-bench、WebArena 等资料补充扩展。

整体写作规划见：[Agent 基础知识系列规划](docs/series-plan.md)。文档之间的结构关系见：[Document Graph](docs/document-graph.md)。

三条推荐入口：

- 从零理解 Agent：[Start Here 路线 A](docs/start-here.md#路线-a从零理解-agent)。
- 从工程落地理解 Agent：[Start Here 路线 B](docs/start-here.md#路线-b从工程落地理解-agent)。
- 从完整案例理解 Agent：[Start Here 路线 C](docs/start-here.md#路线-c从个性化投研-agent-labs-理解完整系统)。

术语统一入口：[Glossary](docs/glossary.md)。

## Stage 1: Agent 基础知识

| 序号 | 主题 | 笔记 |
| --- | --- | --- |
| 01 | Workflow vs Agent | [不要一上来就选 Agent，先分清 Workflow 和 Agent](docs/foundations/01-workflow-vs-agent.md) |
| 02 | Agent Loop | [模型是怎么“边看边干活”的](docs/foundations/02-agent-loop.md) |
| 03 | Tool Use | [工具不是插件，而是 Agent 的手脚](docs/foundations/03-tool-use.md) |
| 04 | RAG | [让 Agent 基于资料回答，而不是靠感觉](docs/foundations/04-rag.md) |
| 05 | Memory | [短期上下文、长期记忆和反思机制](docs/foundations/05-memory.md) |
| 06 | MCP | [Agent 的 USB-C，工具和数据源的统一接口](docs/foundations/06-mcp.md) |
| 07 | Agent Harness | [真正让 Agent 可靠的不是模型，是工程底座](docs/foundations/07-agent-harness.md) |
| 08 | Coding Agent | [为什么代码库是 Agent 最好的训练场](docs/foundations/08-coding-agent.md) |
| 09 | Subagent / Multi-Agent | [多 Agent 不是聊天群，而是上下文隔离和任务分工](docs/foundations/09-subagent-multi-agent.md) |
| 10 | Skills | [把提示词升级成可复用能力包](docs/foundations/10-skills.md) |
| 11 | Browser / Computer Use Agent | [当 Agent 开始操作网页和电脑](docs/foundations/11-browser-computer-use-agent.md) |
| 12 | Evaluation / Trace / Safety | [没有评测和权限边界的 Agent 只是 Demo](docs/foundations/12-evaluation-trace-safety.md) |

## Stage 2: 经典资料精读

后续会把论文、官方文档、工程博客拆成结构化阅读笔记，重点记录：

- 这篇资料解决什么问题。
- 它适合 Agent 系统里的哪个模块。
- 对真实工程有什么启发。
- 有哪些限制和容易误用的地方。

入口：[readings](docs/readings/README.md)。

## Stage 3: 个性化投研 Agent Labs

`labs/` 围绕一个连续场景展开：用户用自然语言描述投资研究策略，系统解析策略、规划投研流程、调用 mock 或真实财经工具、生成带证据和风险提示的观察池报告，并把稳定流程沉淀为 Skill。

当前可运行：

- [Lab 01: Strategy Intake + Workflow/Agent Router](labs/01-strategy-intake/README.md)
  - 规则基线解析和 `routing_decision`。
  - 展示 workflow / agent / needs_clarification / blocked 的判断原因。
  - 可配置模型解析模式和本地 Web demo。
- [Lab 02: Strategy Agent Loop](labs/02-strategy-agent-loop/README.md)
  - 最小 Observe-Decide-Act Loop。
  - mock 投研计划生成。
  - trace、阻断和 max-turn 保护。
- [Lab 03: Finance Tool Use Mock](labs/03-finance-tool-use-mock/README.md)
  - mock 财经工具注册、选择、入参和返回。
  - `tool_trace` 和 `candidate_evidence`。
  - 只生成 mock 观察池证据，不生成投资建议。

完整设计：

- [个性化投研 Agent 产品案例入口](docs/product/README.md)
- [个性化投资调研 Agent 系统愿景](docs/product/personalized-investment-research-agent.md)
- [Agent 学习展示框架](docs/product/showcase-framework.md)
- [个性化投研 Agent Lab 总计划](docs/product/lab-plan.md)
- [密钥、安全与合规边界](docs/product/security-and-secrets.md)

启动 Lab 01 网页 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-web.ps1 -Lab 01-strategy-intake -Port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

运行全部 Lab 测试：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## Stage 4: Agent 工程化

后续重点沉淀：

- 权限控制。
- 工具边界。
- 上下文管理。
- 运行日志。
- 评测体系。
- 成本与延迟优化。
- 人机协同工作流。

入口：[engineering](docs/engineering/README.md)。

## 仓库结构

```text
.
├── README.md
├── AGENTS.md
├── TODO.md
├── roadmap.md
├── .agents/
├── .codex/
├── .env.example
├── docs/
├── hooks/
├── labs/
├── resources/
├── scripts/
└── skills/
```

## 维护原则

- 每篇笔记尽量回答一个明确问题。
- 概念解释和工程实践分开沉淀。
- 先用最小例子讲清楚，再扩展复杂系统。
- 所有实验尽量可运行、可复现、可测试。
- 避免把 Agent 神秘化，优先讨论边界、成本和可靠性。
- 投研 Labs 可以输出候选股票和观察池，但必须给出数据来源、风险提示和人工确认边界。
- 真实密钥只通过环境变量读取，仓库只保留 `.env.example`。
- 新增或重写文档后按 `hooks/content-update.md` 同步导航、更新文档图，并运行内容检查、密钥检查和相关文档审核。
- 新增可运行 Lab 时同步提供 demo 和 tests，并用 `scripts/run-lab-tests.ps1` 做统一回归。
- Codex 维护规则见 [AGENTS.md](AGENTS.md)，可复用工作流见 `.agents/skills/`。
- 当前待办统一维护在 [TODO.md](TODO.md)，需要公开协作时再转成 GitHub Issue。

## 推荐阅读

- [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub)
- Anthropic: Building Effective Agents
- OpenAI Agents SDK documentation
- Model Context Protocol documentation
- LangGraph documentation
- LlamaIndex documentation
- 东方财富妙想 Skills
- 小米 MiMo
