# Agent 学习展示框架

这个文档定义 `Learning_Agent` 的整体可运行展示系统：用一个个性化投研场景，把 Agent 的任务理解、路由、循环、工具调用、RAG、Memory、Skills、Planner、证据报告、Evaluation 和 Safety 串成可观察、可测试、可复盘的学习路径。

投研只是贯穿案例，不是投资建议系统。本仓库不承诺收益，不输出确定性涨跌判断，不绕过人工确认执行交易，也不把真实 key 写入仓库。

## 一、展示系统目标

展示系统的目标不是“做一个能荐股的应用”，而是回答一个学习问题：一个 Agent 系统如何从自然语言任务出发，逐步完成理解、规划、调用工具、引用证据、记住偏好、沉淀 Skill、生成报告，并在每一步保留安全边界。

读者应该能在每个 Lab 里看到：

- 当前展示的是哪个 Agent 概念。
- 用户输入如何被结构化。
- 系统为什么选择某条路径。
- 中间状态、工具调用、证据和 guardrail 如何被记录。
- 高风险或信息不足时为什么要停止、追问或要求人工确认。

财经输出只用于学习演示和观察池构造。未来即使接入真实财经数据源，也必须保留来源、检索时间、风险提示和人工确认边界。

## 二、仓库五层结构

| 层级 | 主要位置 | 作用 |
| --- | --- | --- |
| 学习入口层 | `README.md`, `docs/start-here.md`, `docs/glossary.md` | 帮读者选择路线、统一术语、找到可运行入口。 |
| 概念文章层 | `docs/foundations/` | 解释 Workflow vs Agent、Agent Loop、Tool Use、RAG、Memory、MCP、Skills、Evaluation 等基础概念。 |
| 贯穿案例层 | `docs/product/` | 固化个性化投研 Agent 的愿景、展示框架、Lab 计划和安全边界。 |
| 可运行展示层 | `labs/` | 用 mock-first 的 Lab 把每个概念做成 demo、tests 和可观察输出。 |
| 工程资产层 | `scripts/`, `hooks/`, `docs/maintenance/`, `AGENTS.md` | 提供检查脚本、内容同步规则、仓库规则和可复用维护模板。 |

## 三、展示 Parts 总览

| Part | 对应 Lab | 对应文章 | 展示概念 | 当前状态 |
| --- | --- | --- | --- | --- |
| Part 0 Showcase Overview | 产品文档 | `docs/product/showcase-framework.md` | 展示框架、仓库结构、统一契约 | 已固化 |
| Part 1 Strategy Intake & Router | Lab 01 | 01 Workflow vs Agent | StrategySpec、Workflow/Agent Router、routing_decision | 已实现 |
| Part 2 Agent Loop & Structured Trace | Lab 02 | 02 Agent Loop | observe -> decide -> act、structured trace、fail closed | 已补强 structured trace |
| Part 3 Finance Tool Use Mock | Lab 03 | 03 Tool Use | mock 财经工具注册、选择、入参、返回和失败处理 | 已实现 |
| Part 4 Research RAG Basic | Lab 04 | 04 RAG | 从规则、资料片段和报告模板检索依据 | 已实现 |
| Part 5 User Preference Memory | Lab 05 | 05 Memory | 用户风险偏好、排除条件和观察池偏好的记忆 | 已实现 |
| Part 6 Skill Registry | Lab 06 | 10 Skills | Skill 元数据、能力声明、选择机制和禁用边界 | 已实现 |
| Part 7 Skill Generation | Lab 07 | 10 Skills | 从稳定流程生成可审查 `SKILL.md` 草稿 | 已实现 |
| Part 8 Finance Provider Adapter | Lab 08 | 06 MCP / 03 Tool Use | 外部财经 provider 的 mock-first adapter、optional external provider 和 manual integration 边界 | 增强中 |
| Part 9 Research Planner DAG | Lab 09 | 07 Agent Harness | 从线性计划升级到 DAG 研究计划 | 计划中 |
| Part 10 Evidence Report | Lab 10 | 12 Evaluation / Trace / Safety | 带来源、时间、证据和限制条件的报告 | 计划中 |
| Part 11 Simulation Portfolio & HITL | Lab 11 | 07 Agent Harness / 12 Evaluation | 模拟组合、人工确认、权限边界 | 计划中 |
| Part 12 Evaluation & Safety | Lab 12 | 12 Evaluation / Trace / Safety | 回归评测、密钥检查、风险边界和越权检测 | 计划中 |

## 四、每个 Part 的设计

### Part 0 Showcase Overview

- 展示目标：让读者先理解整个系统为什么存在、各 Lab 如何递进、哪些边界永远不能越过。
- 输入：仓库文档、Lab 计划、安全边界、TODO 和 roadmap。
- 核心输出：展示框架、统一契约、实现顺序和跨文档同步要求。
- 读者应该观察什么：投研案例只是教学载体，真正的主线是 Agent 能力如何逐步拆开。
- 不做什么：不写实验代码，不接真实工具，不生成股票名单。
- 验收标准：产品 README、Start Here、Document Graph、roadmap、TODO 和审计脚本都能找到本文。

### Part 1 Strategy Intake & Router

- 展示目标：把自然语言策略请求转成 `StrategySpec`，并解释为什么走 workflow、agent、needs_clarification 或 blocked。
- 输入：用户的一句话或一段策略描述，例如行业、时间窗、风险过滤和输出目标。
- 核心输出：`StrategySpec`、`routing_decision`、`matched_signals`、`not_selected`、风险提示。
- 读者应该观察什么：同一输入如何被结构化，简单任务为什么可走 workflow，复杂任务为什么需要 agent。
- 不做什么：不查行情，不生成真实股票名单，不调用财经工具。
- 验收标准：四类样例保留；规则基线和可配置模型解析都可运行；默认测试不需要真实 key。

### Part 2 Agent Loop & Structured Trace

- 展示目标：把 `StrategySpec` 放入最小 Agent Loop，展示 observation、decision、action、result 和下一步提示。
- 输入：来自 Lab 01 的 `StrategySpec` 或等价 mock 输入。
- 核心输出：结构化 `TraceEvent` 列表、mock 投研计划、fail-closed 状态。
- 读者应该观察什么：系统每轮看到了什么、为什么这样决策、采取了什么动作、是否触发 guardrail。
- 不做什么：不连接真实工具，不查真实行情，不输出候选股票。
- 验收标准：trace 字段完整；缺信息、高风险和 `max_turns` 都 fail closed；demo 和 tests 都可复现。

### Part 3 Finance Tool Use Mock

- 展示目标：展示 Agent 如何选择财经工具、组织入参、处理返回、记录失败，并把结果变成证据。
- 输入：已通过安全边界的 `StrategySpec`、mock 股票池、mock 行情、mock 新闻。
- 核心输出：`ToolCall`、候选观察池草案、工具错误记录、风险提示。
- 读者应该观察什么：工具不是“魔法答案”，而是有 schema、权限、失败路径和证据引用的外部能力。
- 不做什么：不调用真实东方财富接口，不输出买卖建议，不承诺筛选结果有效。
- 验收标准：mock 工具覆盖成功、空结果、超时、参数错误；所有输出带来源和 `risk_disclosure`。

### Part 4 Research RAG Basic

- 展示目标：展示系统如何从策略规则、风险规则、报告模板和资料片段中检索依据。
- 输入：`StrategySpec`、查询意图、mock 文档库。
- 核心输出：`retrieval_trace`、`retrieved_context`、带引用的 `augmented_evidence`、缺口说明。
- 读者应该观察什么：RAG 的价值是把回答锚定到资料，而不是让模型凭感觉补全。
- 不做什么：不把检索片段当作绝对事实，不引用无来源材料，不抓取未声明的数据源。
- 验收标准：每条检索片段都有 `source`、`chunk_id`、`matched_terms` 和 `used_for`；上游 blocked 时不进入正常检索；测试覆盖文档加载、关键词命中和输出边界。

### Part 5 User Preference Memory

- 展示目标：展示如何保存和读取用户偏好，例如风险等级、排除行业、观察池数量和报告格式。
- 输入：用户偏好、历史交互摘要、当前 `StrategySpec`。
- 核心输出：`memory_snapshot`、`memory_trace`、`effective_user_profile`、`preference_application` 和 `preference_adjusted_evidence`。
- 读者应该观察什么：Memory 是受边界约束的上下文资产，不是无限制保存个人信息。
- 不做什么：不保存真实敏感身份信息，不把历史偏好当成自动交易授权。
- 验收标准：偏好可读、可覆盖、可解释；Memory 只调整证据视图，不修改原始 evidence、来源或 `risk_disclosure`；测试不依赖真实用户数据。

### Part 6 Skill Registry

- 展示目标：展示如何把稳定能力注册为 Skill，并用元数据描述触发场景、输入、输出、禁用场景和人工确认边界。
- 输入：Lab 05 的 Memory + RAG + Evidence 输出、本地 mock Skill 元数据、用户任务。
- 核心输出：`registered_skills`、`skill_selection_trace`、`selected_skills`、`disabled_skills`。
- 读者应该观察什么：Skill 是可复用能力的边界说明，不是把所有提示词堆在一起；选择和禁用都需要可解释。
- 不做什么：不使用 `.agents/` 或 `.codex/` 作为仓库内容，不自动启用高风险 Skill，不把真实 key 写进 Skill，不执行交易动作。
- 验收标准：每个 mock Skill 有 name、description、triggers、disabled_when、inputs、outputs、requires_human_confirmation；blocked、证据不足、缺少风险提示或需要人工确认时禁用相应 Skill；选择过程可追踪且测试可复现。

### Part 7 Skill Generation

- 展示目标：展示如何从稳定流程生成可审查的 `SKILL.md` 草稿，并保留人工审查入口。
- 输入：Lab 06 的 `selected_skills`、`disabled_skills`、`skill_selection_trace` 和上游 evidence。
- 核心输出：`generated_skill_draft`、`skill_draft_markdown`、`draft_review`。
- 读者应该观察什么：从流程到 Skill 是“固化能力”，不是让模型随意扩权；draft 和正式启用之间必须有人类审核。
- 不做什么：不生成带真实 key、真实账户、自动交易权限的 Skill；不写入 `.agents/` 或 `.codex/`；不自动启用。
- 验收标准：生成内容标记 `DRAFT` 且可审阅；包含触发场景、禁用场景、输入、输出、步骤、人工确认点、安全边界、风险提示和测试样例；blocked 请求不生成可启用 Skill。

### Part 8 Finance Provider Adapter

- 展示目标：展示如何把 mock 工具和未来可选外部财经 provider 放到统一 adapter contract 下，同时保持默认 mock 可跑；MX Skills 只是 `mx-skills` provider profile。
- 输入：Lab 07 输出、Lab 03 mock finance tools、adapter capabilities 和安全门规则。
- 核心输出：`registered_adapters`、`adapter_mode`、`provider_mode`、`adapter_trace`、`safety_gate`、`real_provider_attempted`、`real_provider_allowed`。
- 读者应该观察什么：真实数据源只是在边界内替换 provider，不能改变风险、人工确认和测试默认 mock 的规则。
- 不做什么：不读取真实 key，除非用户同时打开 CLI 和环境变量安全门；不默认访问真实服务，不发送网络请求，不绕过 mock 测试，不使用 `.agents/` 或 `.codex/`。
- 验收标准：mock adapter 能调用 `candidate-screen`、`market-data`、`finance-news`；`external-finance-stub` 调用时 blocked；`external-finance` 缺少任一启用条件时 blocked 且不发请求；fake transport 能验证外部 provider 成功路径；manual integration test 默认跳过；输出保留风险提示且默认测试无 key 通过。

### Part 9 Research Planner DAG

- 展示目标：把线性投研计划升级为 DAG，展示任务依赖、并行分支、失败传播和重试边界。
- 输入：`StrategySpec`、可用工具、检索能力、用户偏好。
- 核心输出：Research Planner DAG、节点状态、依赖关系、跳过原因。
- 读者应该观察什么：Planner 不是简单待办列表，而是带依赖、状态和退出条件的执行图。
- 不做什么：不让计划绕过安全节点，不把失败节点静默忽略。
- 验收标准：DAG 可视化；节点状态可追踪；阻断、重试和跳过都有原因。

### Part 10 Evidence Report

- 展示目标：把工具结果、检索片段和风险判断组织成可审查的投研观察报告。
- 输入：`StrategySpec`、`TraceEvent`、`ToolCall`、`EvidenceItem`、`SafetyDecision`。
- 核心输出：证据报告、观察池、限制条件、风险提示、人工确认事项。
- 读者应该观察什么：报告价值来自可追溯证据和不确定性表达，而不是“结论看起来像真的”。
- 不做什么：不输出保证收益、确定涨跌、买入卖出指令。
- 验收标准：每个候选观察项都有证据引用；报告包含时间、来源、限制和风险提示。

### Part 11 Simulation Portfolio & HITL

- 展示目标：展示模拟组合或观察池变更为什么必须经过人工确认。
- 输入：报告候选项、模拟组合状态、用户确认或拒绝。
- 核心输出：待确认动作、确认记录、模拟执行结果、撤销或拒绝原因。
- 读者应该观察什么：HITL 是系统边界的一部分，不是界面上的“确认按钮”装饰。
- 不做什么：不接真实交易，不自动买卖，不把用户一次确认扩展成长期授权。
- 验收标准：所有高风险动作都有确认记录；拒绝和取消路径可测试；默认 mock-first。

### Part 12 Evaluation & Safety

- 展示目标：建立贯穿所有 Lab 的回归评测、安全检查和内容边界审计。
- 输入：测试样例、trace、报告、文档和配置文件。
- 核心输出：`EvalResult`、失败用例、风险分类、修复建议。
- 读者应该观察什么：Agent 系统不是“能跑一次”就完成，而是要持续证明边界没有被破坏。
- 不做什么：不把评测只做成最终答案检查，不允许密钥或敏感凭据进入仓库。
- 验收标准：检查脚本可重复运行；高风险输出被拦截；文档同步和 Lab 测试纳入常规维护。

## 五、统一数据契约

这些契约只做文档级字段说明，具体实现可以在各 Lab 中按需要演进，但字段含义应保持一致。

### StrategySpec

| 字段 | 说明 |
| --- | --- |
| `original_request` | 用户原始自然语言请求。 |
| `market` | 市场范围，例如 A 股、港股、美股或未指定。 |
| `themes` | 用户关注的行业、主题或方向。 |
| `horizon_days` | 观察周期或回看窗口。 |
| `candidate_rules` | 候选观察池的筛选规则。 |
| `risk_filters` | 回撤、负面新闻、流动性、合规等过滤条件。 |
| `user_preferences` | 用户偏好引用或本次输入中的偏好。 |
| `output` | 期望输出类型，例如流程计划、观察池、报告。 |
| `execution_mode` | `workflow`、`agent`、`needs_clarification` 或 `blocked`。 |
| `requires_agent` | 是否需要多步判断、工具反馈或不确定性处理。 |
| `routing_decision` | 路由判断对象或引用。 |
| `clarification_questions` | 信息不足时需要追问的问题。 |
| `prohibited_actions` | 被安全边界禁止的动作。 |
| `risk_disclosure` | 必须展示的风险提示。 |

### RoutingDecision

| 字段 | 说明 |
| --- | --- |
| `mode` | 路由结果：workflow、agent、needs_clarification、blocked。 |
| `reason` | 选择该路径的简短原因。 |
| `matched_signals` | 命中的判断信号。 |
| `not_selected` | 未选择其他路径的原因。 |
| `next_step` | 下一步建议，例如进入 Agent Loop、追问或停止。 |

### TraceEvent

| 字段 | 说明 |
| --- | --- |
| `turn` | 循环轮次。 |
| `observation` | 当前观察到的状态、输入或工具结果。 |
| `decision` | 本轮选择的决策。 |
| `why_this_action` | 为什么采取该动作。 |
| `action` | 本轮动作，例如生成计划、调用 mock 工具、追问或停止。 |
| `result` | 动作结果。 |
| `guardrail_triggered` | 是否触发 guardrail，以及触发了什么。 |
| `next_action_hint` | 下一步提示。 |
| `status` | running、completed、needs_clarification、blocked、failed 等状态。 |

### ToolCall

| 字段 | 说明 |
| --- | --- |
| `tool_name` | 工具名称。 |
| `provider` | 工具来源，例如 mock、mx-style adapter 或 future real provider。 |
| `input` | 结构化入参。 |
| `output` | 工具返回结果摘要。 |
| `status` | success、empty、failed、timeout、blocked。 |
| `error` | 失败或降级原因。 |
| `evidence_refs` | 生成的证据引用。 |
| `trace_id` | 关联的 trace 事件。 |

### EvidenceItem

| 字段 | 说明 |
| --- | --- |
| `evidence_id` | 证据唯一标识。 |
| `source_type` | 来源类型，例如 mock_data、news、report、policy、template。 |
| `source_name` | 来源名称或文件路径。 |
| `fetched_at` | 获取或生成时间。 |
| `subject` | 证据对应的主题、公司、行业或规则。 |
| `claim` | 证据支持或反驳的说法。 |
| `value` | 关键数值、摘要或片段。 |
| `confidence` | 置信度或质量等级。 |
| `limitations` | 限制条件和不确定性。 |

### SafetyDecision

| 字段 | 说明 |
| --- | --- |
| `allowed` | 是否允许继续。 |
| `reason` | 允许、阻断或要求确认的原因。 |
| `triggered_rules` | 命中的安全规则。 |
| `required_human_confirmation` | 是否需要人工确认。 |
| `redactions` | 需要脱敏或隐藏的字段。 |
| `risk_disclosure` | 对用户展示的风险提示。 |

### EvalResult

| 字段 | 说明 |
| --- | --- |
| `case_id` | 评测样例编号。 |
| `target_part` | 评测覆盖的 Part 或 Lab。 |
| `passed` | 是否通过。 |
| `score` | 可选分数或等级。 |
| `failures` | 失败原因列表。 |
| `trace_refs` | 关联 trace 或日志。 |
| `regression_note` | 回归风险和修复说明。 |

## 六、统一展示原则

- 不只看最终结果，要展示中间状态、路由理由、工具调用、证据和安全判断。
- 每个 Lab 都必须说明对应哪个 Agent 概念。
- 每个 Lab 都必须有 README、demo 和 tests。
- 默认 mock 可跑，默认测试不依赖真实 key、真实账户或真实外部服务。
- 真实 key 只能从环境变量读取，仓库只保留 `.env.example` 占位。
- 投研输出必须带来源、检索时间、限制条件、风险提示和人工确认边界。
- 高风险动作必须人工确认，且确认不能被扩展成自动交易授权。
- 缺信息、高风险、越权请求、密钥泄露风险和 max-turn 超限都要 fail closed。
- 每次修改 Product、Labs、Skills 或 Docs 后，同步相关 README、Document Graph、roadmap、TODO，并运行检查脚本。

## 七、实现顺序

| Phase | 范围 | 目标 |
| --- | --- | --- |
| Phase 1 | Lab 01 / Lab 02 教学表达修正 | 让 StrategySpec、routing_decision、Agent Loop 和 structured trace 更容易观察。 |
| Phase 2 | Lab 03 Tool Use Mock | 建立 mock 财经工具、ToolCall、错误处理和证据引用。 |
| Phase 3 | RAG + Memory | 引入资料检索、证据片段、用户偏好和冲突处理。 |
| Phase 4 | Skills | 建立 Skill Registry，并从稳定流程生成可审查的 Skill 草稿。 |
| Phase 5 | Planner + Evidence Report | 把研究流程升级为 DAG，并生成带来源和限制条件的报告。 |
| Phase 6 | Evaluation + Safety | 统一回归评测、安全审计、风险提示和人工确认边界。 |
