# Product Case: 个性化投研 Agent

这里是 `Agent基础知识` 系列的连续实践案例入口。个性化投研 Agent 不是为了把仓库变成荐股系统，而是用一个足够真实、边界清晰、可测试的场景，把 Agent 的核心概念串成一条可运行的学习路径。

## 为什么选择这个案例

| Agent 概念 | 投研案例中的对应问题 |
| --- | --- |
| Workflow vs Agent | 哪些策略可以走固定流程，哪些策略需要多步骤判断和工具反馈。 |
| Agent Loop | 系统如何观察当前策略状态、决定下一步、执行动作并记录 trace。 |
| Tool Use | 如何调用候选筛选、行情数据、资讯搜索等工具，并把结果纳入证据。 |
| RAG | 如何从风险规则、报告模板和资料片段中检索依据。 |
| Memory | 如何记住用户风险偏好、排除行业和候选数量。 |
| MCP / Skills | 如何把财经工具和稳定流程注册成可复用能力。 |
| Evaluation / Safety | 如何检查风险提示、来源、人工确认和密钥边界。 |

这个案例的价值在于：自然语言输入复杂、需要多步骤流程、需要证据、需要偏好和安全边界。它适合展示 Agent 系统设计，但所有财经输出都只用于学习演示和观察池。

## 文档阅读顺序

1. [Start Here](../start-here.md): 先选择学习路径。
2. [个性化投资调研 Agent 系统愿景](personalized-investment-research-agent.md): 理解系统想做什么、边界在哪里。
3. [Agent 学习展示框架](showcase-framework.md): 理解 Parts 0-12 如何把 Agent 概念串成可运行展示系统。
4. [Lab 总计划](lab-plan.md): 看 12 篇基础文章如何映射到 12 个 Labs。
5. [密钥、安全与合规边界](security-and-secrets.md): 先明确真实 key、财经输出和人工确认规则。
6. [Labs 入口](../../labs/README.md): 进入当前可运行实验。

## 当前做到哪里

| Lab | 状态 | 当前展示 |
| --- | --- | --- |
| [Lab 01: Strategy Intake + Workflow/Agent Router](../../labs/01-strategy-intake/README.md) | 已实现 | 把自然语言策略解析成 `StrategySpec` 和 `routing_decision`，支持规则基线和可配置模型语义补全。 |
| [Lab 02: Strategy Agent Loop](../../labs/02-strategy-agent-loop/README.md) | 已实现 | 把 `StrategySpec` 放进最小 Agent Loop，生成 mock 投研计划并记录 trace。 |
| [Lab 03: Finance Tool Use Mock](../../labs/03-finance-tool-use-mock/README.md) | 已实现 | 用 mock `mx-xuangu`、`mx-data`、`mx-search` 风格工具展示工具调用、`tool_trace` 和 `candidate_evidence`。 |
| [Lab 04: Research RAG Basic](../../labs/04-research-rag-basic/README.md) | 已实现 | 用本地 markdown 知识库展示 RAG，生成 `retrieval_trace`、`retrieved_context` 和 `augmented_evidence`。 |
| [Lab 05: User Preference Memory](../../labs/05-user-preference-memory/README.md) | 已实现 | 用本地 mock 用户偏好展示 Memory，生成 `memory_trace` 和 `preference_adjusted_evidence`。 |

## Lab 03-12 简短路线

| Lab | 主题 | 目标 |
| --- | --- | --- |
| 03 | Finance Tool Use Mock | 跑通 mock 财经工具注册、选择、入参、返回、失败和 trace。 |
| 04 | Research RAG Basic | 检索策略规则、风险规则和报告模板，并挂回 Lab 03 的 mock 证据。 |
| 05 | User Preference Memory | 记住风险偏好、排除条件和候选数量，并只调整证据视图。 |
| 06 | Skill Registry | 建立 Skill 元数据和选择机制。 |
| 07 | Skill Generation | 从稳定流程生成 `SKILL.md` 草稿。 |
| 08 | MX Skills Adapter | 将 mock 工具适配到东方财富妙想 Skills。 |
| 09 | Research Planner | 将线性计划升级成有状态 DAG。 |
| 10 | Evidence Report | 生成带来源、时间、证据和风险提示的报告。 |
| 11 | Simulation Portfolio | 用 mock 或模拟组合接口验证流程，保留人工确认。 |
| 12 | Evaluation & Safety | 自动检查密钥、证据、风险提示和越权动作。 |

## 财经输出边界

- 仅用于学习演示和观察池，不构成投资建议或收益承诺。
- 可以生成候选观察池，但必须说明数据来源、检索时间、证据和不确定性。
- 不输出保证收益、稳赚、必涨等确定性表述。
- 不绕过人工确认执行自选股、模拟组合、Skill 启用或任何交易相关动作。
- 不提交真实 API key、token、cookie、账户凭据或个人隐私。

## 当前可运行入口

启动 Lab 01 网页 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-web.ps1 -Lab 01-strategy-intake -Port 8765
```

运行 Lab 01 / Lab 02 / Lab 03 / Lab 04 / Lab 05 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 02-strategy-agent-loop
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 03-finance-tool-use-mock
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 04-research-rag-basic
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 05-user-preference-memory
```

运行全部 Lab 测试：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
