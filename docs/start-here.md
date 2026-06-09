# Start Here

这个仓库是一个面向后端工程师和 Agent 初学者的学习入口：先用 12 篇基础文章建立概念，再用一个连续的个性化投研 Agent 案例，把 Agent Loop、Tool Use、RAG、Memory、Skills、Evaluation 和 Safety 跑成可观察、可测试、可复盘的实验。

## 适合谁

- 想从零理解 Agent、Workflow、Tool Use、RAG、Memory、MCP、Skills 等基础概念的人。
- 想知道 Agent 如何从文章概念落到可运行实验、trace、测试和安全边界的人。
- 想用一个连续案例理解 Agent 系统设计，但不希望一开始就陷入复杂框架的人。
- 想维护一套可长期扩展的 Agent 学习仓库、Lab 和 Skill 示例的人。

## 路线 A：从零理解 Agent

适合先打概念基础，再看最小实验。

阅读顺序：

1. [01 Workflow vs Agent](foundations/01-workflow-vs-agent.md)
2. [02 Agent Loop](foundations/02-agent-loop.md)
3. [03 Tool Use](foundations/03-tool-use.md)
4. [Glossary](glossary.md)
5. [Lab 01: Strategy Intake + Workflow/Agent Router](../labs/01-strategy-intake/README.md)
6. [Lab 02: Strategy Agent Loop](../labs/02-strategy-agent-loop/README.md)

可运行命令：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 02-strategy-agent-loop
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

观察重点：

- Lab 01 如何把自然语言策略转成 `StrategySpec`，并用 `routing_decision` 展示 workflow / agent / clarification / blocked 的判断原因。
- Lab 02 如何把 `StrategySpec` 放进 observe -> decide -> act 的循环。
- 高风险或缺信息输入为什么会被阻断或追问。

## 路线 B：从工程落地理解 Agent

适合已经知道大概概念，想看 Agent 系统为什么需要工程底座。

阅读顺序：

1. [07 Agent Harness](foundations/07-agent-harness.md)
2. [08 Coding Agent](foundations/08-coding-agent.md)
3. [12 Evaluation / Trace / Safety](foundations/12-evaluation-trace-safety.md)
4. [Engineering](engineering/README.md)
5. [密钥、安全与合规边界](product/security-and-secrets.md)
6. [Document Graph](document-graph.md)

可运行命令：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

观察重点：

- trace 和测试如何让 demo 具备回归能力。
- 密钥、安全边界和人工确认为什么从第一天就要进入设计。
- 文档图和审核脚本如何减少长期维护时的遗漏。

## 路线 C：从个性化投研 Agent Labs 理解完整系统

适合直接沿着一个连续案例理解 Agent 系统如何逐步长出来。

阅读顺序：

1. [产品案例入口](product/README.md)
2. [个性化投资调研 Agent 系统愿景](product/personalized-investment-research-agent.md)
3. [Agent 学习展示框架](product/showcase-framework.md)
4. [个性化投研 Agent Lab 总计划](product/lab-plan.md)
5. [Labs 入口](../labs/README.md)
6. [Lab 01: Strategy Intake + Workflow/Agent Router](../labs/01-strategy-intake/README.md)
7. [Lab 02: Strategy Agent Loop](../labs/02-strategy-agent-loop/README.md)
8. [Lab 03: Finance Tool Use Mock](../labs/03-finance-tool-use-mock/README.md)

启动 Lab 01 网页 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-web.ps1 -Lab 01-strategy-intake -Port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

观察重点：

- 投研只是贯穿案例，核心是学习 Agent 的任务理解、循环执行、工具调用、证据收集、记忆、Skill 固化和安全评测。
- 展示框架把 Parts 0-12 统一起来，说明每个 Lab 的输入、输出、观察点、边界和验收标准。
- Lab 01 / Lab 02 / Lab 03 不生成真实股票名单，也不执行交易。
- Lab 03 用 mock 工具展示工具注册、入参、返回、失败、`tool_trace` 和 `candidate_evidence`。

## 当前可运行

| Lab | 展示概念 | 运行方式 |
| --- | --- | --- |
| [Lab 01: Strategy Intake + Workflow/Agent Router](../labs/01-strategy-intake/README.md) | 自然语言策略解析、`routing_decision`、规则基线、可配置模型语义补全、安全边界 | `powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake` |
| [Lab 02: Strategy Agent Loop](../labs/02-strategy-agent-loop/README.md) | 最小 Agent Loop、trace、阻断、max-turn 保护 | `powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 02-strategy-agent-loop` |
| [Lab 03: Finance Tool Use Mock](../labs/03-finance-tool-use-mock/README.md) | mock 工具注册、工具选择、`tool_trace`、`candidate_evidence` | `powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 03-finance-tool-use-mock` |

当前继续方向：

- 进入 Lab 04: Research RAG Basic，把 Lab 03 的 mock evidence 接入本地资料检索、规则片段和报告模板。
- 默认测试不依赖真实 key。

## 安全边界

- 本仓库中的投研内容仅用于学习演示和观察池，不构成投资建议或收益承诺。
- 不提交真实 API key、token、cookie、session、账户信息或个人隐私。
- 默认测试使用 mock 数据和 mock 模型响应。
- 真实模型 provider 或东方财富妙想 Skills 只能从 Hermes 或受信任的本地环境注入。
- 涉及候选股票、观察池、模拟组合或 Skill 启用时，必须保留风险提示和人工确认边界。
