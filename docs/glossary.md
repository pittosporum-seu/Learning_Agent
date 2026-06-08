# Glossary

这个术语表用于统一 `Learning_Agent` 仓库里的核心概念。建议第一次阅读基础文章或运行 Labs 前先扫一遍，之后遇到不熟悉的词再回来查。

| 术语 | 中文解释 | 解决什么问题 | 建议阅读 |
| --- | --- | --- | --- |
| Agent | 能根据目标、上下文和环境反馈自主选择下一步动作的系统 | 处理无法预先完全写死路径的任务 | [02 Agent Loop](foundations/02-agent-loop.md) |
| Workflow | 预先定义好步骤和分支的确定性流程 | 处理规则明确、路径稳定、可预测的任务 | [01 Workflow vs Agent](foundations/01-workflow-vs-agent.md) |
| Agent Loop | Agent 反复观察、决策、行动、接收结果的循环 | 让系统根据中间结果调整行为，而不是一次性输出 | [02 Agent Loop](foundations/02-agent-loop.md) |
| Tool Use | 模型通过宿主程序调用外部工具、函数、API 或脚本 | 让 Agent 获取数据、执行动作、验证结果 | [03 Tool Use](foundations/03-tool-use.md) |
| RAG | Retrieval-Augmented Generation，检索增强生成 | 让回答基于资料和证据，而不是只靠模型记忆 | [04 RAG](foundations/04-rag.md) |
| Memory | Agent 对用户偏好、历史任务、长期事实或短期状态的记忆机制 | 让系统跨轮次保留有用信息，并能解释和清除 | [05 Memory](foundations/05-memory.md) |
| MCP | Model Context Protocol，模型上下文协议 | 用统一接口连接工具、数据源和 Agent 宿主 | [06 MCP](foundations/06-mcp.md) |
| Harness | Agent 的工程底座，包括权限、上下文、工具、日志、评测和恢复机制 | 让 Agent 从 demo 变成可控、可测、可维护的系统 | [07 Agent Harness](foundations/07-agent-harness.md) |
| Coding Agent | 面向代码库工作的 Agent，能读写文件、运行命令和根据测试反馈修正 | 在结构化环境中展示 Agent 的工具调用和反馈循环 | [08 Coding Agent](foundations/08-coding-agent.md) |
| Subagent | 被主 Agent 调度、承担特定子任务的隔离 Agent | 分离上下文、降低干扰、并行处理独立问题 | [09 Subagent / Multi-Agent](foundations/09-subagent-multi-agent.md) |
| Skill | 可复用能力包，通常包含触发场景、步骤、脚本、资源和输出规范 | 把稳定流程沉淀成可组合的能力 | [10 Skills](foundations/10-skills.md) |
| Browser Agent | 能观察和操作网页的 Agent | 处理需要浏览、点击、填写、检查页面状态的任务 | [11 Browser / Computer Use Agent](foundations/11-browser-computer-use-agent.md) |
| Computer Use Agent | 能在更通用电脑界面中执行操作的 Agent | 处理浏览器以外的 UI 操作和跨应用任务 | [11 Browser / Computer Use Agent](foundations/11-browser-computer-use-agent.md) |
| Evaluation | 对 Agent 行为、输出质量、安全性和稳定性的评测 | 判断 Agent 是否真的可用，而不是只看单次演示 | [12 Evaluation / Trace / Safety](foundations/12-evaluation-trace-safety.md) |
| Trace | Agent 执行过程中的观察、决策、动作、结果和状态记录 | 让系统行为可调试、可审计、可复盘 | [12 Evaluation / Trace / Safety](foundations/12-evaluation-trace-safety.md) |
| Guardrails | 对输入、工具、输出和权限的保护规则 | 防止越权、泄露密钥、承诺收益或执行危险动作 | [12 Evaluation / Trace / Safety](foundations/12-evaluation-trace-safety.md) |
| HITL | Human-in-the-loop，人类参与确认或审核 | 在高风险动作前保留人工判断和责任边界 | [12 Evaluation / Trace / Safety](foundations/12-evaluation-trace-safety.md) |
| StrategySpec | Lab 01 中的结构化策略对象，包含市场、主题、时间窗、筛选规则、风险过滤和执行模式 | 把自然语言投研想法变成后续 Planner 和工具能使用的输入 | [Lab 01](../labs/01-strategy-intake/README.md) |
| Evidence Store | 存放候选、行情、资讯、规则、引用和报告证据的结构化区域 | 让投研输出能追溯来源，避免无证据结论 | [个性化投研 Agent Lab 总计划](product/lab-plan.md) |
