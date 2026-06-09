# 个性化投研 Agent Lab 总计划

这组 Lab 用一个连续场景贯穿 12 篇 `Agent基础知识`：构建一个个性化投资调研系统。
整体展示框架见：[Agent 学习展示框架](showcase-framework.md)；本文件负责把框架拆成 Lab 顺序和验收节奏。

愿景是：用户用自然语言描述策略，系统生成投研流程规划，逐步调用 Skills 执行；当某个流程稳定后，再固化为可复用 Skill。模型侧采用可配置的 OpenAI-compatible provider，当前 Hermes 示例可映射到小米 MiMo；财经信息源逐步接入东方财富妙想 Skills。测试默认使用 mock，真实 key 只从 Hermes 或受信任的本地环境注入到环境变量。

默认示例策略：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

## 共享案例材料

共享材料放在 `labs/shared/investment_research_case/`：

- `strategy_request.md`: 用户策略样例。
- `strategy_policy.md`: 策略解析和风险边界。
- `risk_policy.md`: 输出风险提示和禁用场景。
- `user_profile.md`: 用户偏好、风险承受能力、排除条件。

后续 Lab 会补充：

- `mock_universe.csv`: mock 股票池。
- `mock_prices.csv`: mock 行情数据。
- `mock_news.md`: mock 新闻、公告、研报摘要。
- `report_template.md`: 证据化报告模板。

## Lab 路线

| Lab | 名称 | 对应文章 | 目标产出 | 状态 |
| --- | --- | --- | --- | --- |
| 01 | Strategy Intake + Workflow/Agent Router | 01 Workflow vs Agent | 自然语言策略转 `StrategySpec` 和 `routing_decision`，解释 workflow / agent / clarification / blocked 的路由原因 | 已实现 |
| 02 | Strategy Agent Loop | 02 Agent Loop | Observe-Decide-Act 循环、trace、阻断、投研计划生成 | 已实现 |
| 03 | Finance Tool Use Mock | 03 Tool Use | mock `mx-xuangu`、`mx-data`、`mx-search` 的工具调用、`tool_trace` 和 `candidate_evidence` | 已实现 |
| 04 | Research RAG Basic | 04 RAG | 本地 markdown 知识库检索、`retrieval_trace`、`retrieved_context` 和 `augmented_evidence` | 已实现 |
| 05 | User Preference Memory | 05 Memory | 本地 mock 用户偏好、`memory_trace`、`preference_application` 和 `preference_adjusted_evidence` | 已实现 |
| 06 | Skill Registry | 06 MCP / 10 Skills | 本地 mock Skill 元数据、`skill_selection_trace`、`selected_skills` 和 `disabled_skills` | 已实现 |
| 07 | Skill Generation | 10 Skills | 从 Lab 06 输出生成 `generated_skill_draft`、`skill_draft_markdown` 和 `draft_review` | 已实现 |
| 08 | MX Skills Adapter | 03 Tool Use / 06 MCP | mock-first adapter contract、`adapter_trace`、`safety_gate`、optional real provider 和 manual integration test | 增强中 |
| 09 | Research Planner | 07 Agent Harness | 生成投研 DAG 并管理步骤状态 | 计划中 |
| 10 | Evidence Report | 04 RAG / 12 Evaluation | 生成带来源、时间、证据和风险提示的报告 | 计划中 |
| 11 | Simulation Portfolio | 11 Browser / Computer Use Agent / Safety | 用 mock 或 `mx-moni` 风格接口做模拟组合验证 | 计划中 |
| 12 | Evaluation & Safety | 12 Evaluation / Trace / Safety | 检查密钥泄露、无证据推荐、风险提示缺失 | 计划中 |

## 统一结构

每个 Lab 目录建议包含：

```text
README.md
demo/
src/
tests/
web/
data/
outputs/
```

`README.md` 固定写清楚：

- 本 Lab 解决什么问题。
- 输入是什么。
- 输出是什么。
- 如何运行 mock 版本。
- 是否有本地 web demo。
- 如何切换真实数据源或真实模型。
- 哪些操作需要人工确认。
- 验收标准是什么。

## Lab 01: Strategy Intake + Workflow/Agent Router

目标：把用户自然语言策略解析成结构化 `StrategySpec`，并把 workflow / agent / needs_clarification / blocked 的路由判断显式展示出来。

关键点：

- 规则基线用于稳定字段、回归测试和边界拦截。
- `routing_decision` 解释命中的判断信号、下一步和为什么不选其他模式。
- 模型模式读取 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL`，真实调用 OpenAI-compatible provider 做语义补全。
- 不在这一层调用真实财经数据，也不生成个股名单。

验收标准：

- 给定策略文本，可以输出稳定 JSON。
- 四类样例能分别路由到 workflow、agent、needs_clarification 和 blocked。
- 缺少关键字段时能提出待确认问题。
- 高风险请求能转为风险边界提示。
- Web demo 能在 `http://127.0.0.1:8765/` 展示规则基线和可配置模型解析两种模式，且默认不调用模型。
- 测试不依赖真实 API key。

## Lab 02: Strategy Agent Loop

目标：让系统具备最小 Agent Loop：观察当前状态、选择下一步、执行一步、记录结果。

关键点：

- 每一轮只做一个清晰动作。
- 状态里保留 `StrategySpec`、研究计划、trace、最终输出和错误。
- `TraceEvent` 固定展示 observation、decision、why_this_action、action、result、guardrail_triggered、next_action_hint 和 status。
- 不完整或不安全请求会阻断并返回追问。
- 有 max-turn 保护，避免循环失控。

验收标准：

- mock 运行能完成一条策略的计划生成。
- 日志可追踪每一步为什么发生。
- structured trace 的 `result` 是结构化对象，并能展示 plan_step_count、planned_tools、requires_human_confirmation 等关键字段。
- workflow 请求和 agent 请求会生成不同计划。
- 风险请求不会进入投研执行计划。

## Lab 03: Finance Tool Use Mock

目标：在不接真实 API 的情况下，把财经工具调用模式跑通。

关键点：

- `select_candidates()` 模拟 `mx-xuangu`。
- `fetch_market_data()` 模拟 `mx-data`。
- `search_finance_news()` 模拟 `mx-search`。
- 工具返回结构化数据，不直接写最终结论。
- 工具调用写入 `tool_trace`，工具结果先转成 `candidate_evidence`，不直接变成投资建议。

验收标准：

- 工具入参、出参稳定。
- 工具失败能被 Agent 捕获。
- 输出包含 `risk_disclosure`，不包含买卖动作、目标价或收益承诺。
- 测试不依赖真实 API key。

## Lab 04: Research RAG Basic

目标：让系统能从策略规则、风险规则、报告模板中检索相关片段，并把这些片段接入 Lab 03 的 `candidate_evidence`。

关键点：

- 先用本地 markdown 文档和简单关键词检索实现。
- `retrieved_context` 必须包含 `source`、`chunk_id`、`matched_terms` 和 `used_for`。
- 上游 Lab 03 blocked 时，本 Lab 不进入正常检索。
- 检索片段只能作为 mock 依据，不生成真实投资建议。

验收标准：

- 报告能列出引用来源。
- 风险规则和报告模板能被检索并参与输出。
- 测试不依赖真实模型、真实向量库或真实财经 API。

## Lab 05: User Preference Memory

目标：让系统读取本地 mock 用户偏好，但不把偏好当成投资结论。

关键点：

- 读取 `conservative_user` 和 `balanced_user` 两个 mock profile。
- Memory 可以影响 `max_candidates`、`excluded_themes`、`excluded_risk_flags` 和 `report_style`。
- Memory 只生成 `preference_adjusted_evidence`，不修改原始 `candidate_evidence`。
- 高风险请求仍然 blocked，不会因为 Memory 继续执行。

验收标准：

- 同一策略在不同用户偏好下输出不同 adjusted view。
- 记忆内容可解释、可查看。
- 测试不依赖真实用户数据、真实模型或真实财经 API。

## Lab 06: Skill Registry

目标：建立可复用 Skill 的注册表，让系统知道什么时候选择哪个能力，以及什么时候必须禁用。

关键点：

- Skill 元数据包含名称、描述、触发条件、输入、输出、禁用场景和人工确认要求。
- 根据 Lab 05 的 Memory + RAG + Evidence 输出构造 selection context。
- 输出 `skill_selection_trace`、`selected_skills` 和 `disabled_skills`，解释每个 Skill 的选择或禁用原因。
- 本 Lab 只使用本地 mock Skill 元数据，不使用 `.agents/` 或 `.codex/` 本地运行配置。
- blocked、证据不足、缺少风险提示或需要人工确认的场景会禁用相应 Skill。

验收标准：

- 系统能根据任务和证据选择合适 mock Skill。
- 禁用场景能阻止不合适调用，并保留可复盘原因。
- 输出包含 `risk_disclosure`，不生成投资建议、真实股票推荐或交易动作。
- 测试不依赖真实模型、真实财经 API、真实用户数据或本地 runtime Skill 配置。

## Lab 07: Skill Generation

目标：把稳定投研流程生成可审查的 `SKILL.md` 草稿，但不自动启用。

关键点：

- 从 Lab 06 的 `selected_skills`、`disabled_skills`、`skill_selection_trace` 和上游 evidence 中提取稳定步骤。
- 生成 `generated_skill_draft` 和类 `SKILL.md` 的 `skill_draft_markdown`，并明确标记 `DRAFT`。
- 草稿写清触发场景、禁用场景、输入、输出、步骤、人工确认点、安全边界和测试样例。
- `draft_review` 检查 `risk_disclosure`、禁用场景、人工 review / confirmation 和禁止字段。
- 新 Skill draft 只进入人工审核，不自动启用，也不写入 `.agents/` 或 `.codex/`。

验收标准：

- 能从一次完整 mock 投研流程生成 Skill draft。
- blocked 请求不会生成可启用 Skill。
- 草稿包含风险提示、禁用场景、人工确认点和测试样例。
- 输出包含 `risk_disclosure`，不生成投资建议、真实股票推荐或交易动作。
- 测试不依赖真实模型、真实财经 API、真实用户数据或本地 runtime Skill 配置。

## Lab 08: MX Skills Adapter

目标：把 Lab 03 的 mock finance tools 和未来真实东方财富妙想 Skills 放到同一 adapter contract 下。

关键点：

- 默认使用 `mock-mx` adapter，复用本地 mock `mx-xuangu`、`mx-data`、`mx-search` 风格能力。
- `real-mx-stub` 只返回 blocked / disabled，不读取真实 key，不发送网络请求。
- `real-mx` 是可选真实 provider 路径，必须同时满足 `--allow-real-provider`、`MX_ALLOW_REAL_PROVIDER=true`、`MX_APIKEY` 和 `MX_SKILLS_BASE_URL` / `MX_BASE_URL`。
- `safety_gate` 明确展示 `real_provider_attempted`、`real_provider_allowed`、`api_key_present`、`network_request_sent` 和 `raw_response_persisted=false`。
- 每次 adapter 调用都生成统一 `AdapterResult`，写入 `adapter_trace`。
- 真实 provider 响应只进入摘要字段，不能保存 raw authenticated response。
- 本 Lab 不使用 `.agents/` 或 `.codex/`，不生成投资建议或交易动作。

验收标准：

- 无密钥时测试通过，默认 mock adapter 可跑。
- mock adapter 能调用 `mx-xuangu`、`mx-data`、`mx-search` 三个能力。
- real adapter stub 调用时 blocked，并说明启用条件。
- real adapter 缺少任一启用条件时 blocked，且不发送网络请求。
- real adapter 可以通过 fake transport 单测成功路径；真实 provider 只能通过手动 integration test 验证。
- 输出包含 `risk_disclosure` 和 `safety_gate`，不生成投资建议、真实股票推荐或交易动作。
- blocked 请求不会调用 adapter。

## Lab 09: Research Planner

目标：把投研流程变成有状态的 DAG。

关键点：

- 候选池生成、行情核验、资讯核验、风险审查、报告生成之间有明确依赖。
- 每个节点有输入、输出、状态和错误处理。
- Planner 可以暂停等待人工确认。

验收标准：

- 同一策略能生成稳定计划。
- 节点失败不会污染后续报告。

## Lab 10: Evidence Report

目标：输出能被人审阅的证据化投研报告。

关键点：

- 每个候选结论都要有来源。
- 报告包含数据日期、检索时间、风险提示和不确定性。
- 候选股票可以推荐进入观察池，但必须说明不是投资建议。

验收标准：

- 报告不出现无来源断言。
- 报告固定包含风险提示。
- 报告能指出需要人工复核的问题。

## Lab 11: Simulation Portfolio

目标：用模拟组合验证观察池或策略执行流程。

关键点：

- 默认 mock 组合。
- 真实 `mx-moni` 只用于模拟组合，不用于真实交易。
- 买入、卖出、撤单类动作必须有人类确认。

验收标准：

- 能查询模拟持仓和资金。
- 能生成模拟执行计划。
- 未确认前不能执行模拟买卖动作。

## Lab 12: Evaluation & Safety

目标：把安全和质量检查变成自动化测试。

关键点：

- 检查真实密钥是否进入仓库。
- 检查报告是否缺少风险提示。
- 检查股票候选是否缺少证据。
- 检查系统是否承诺收益或绕过人工确认。

验收标准：

- `scripts/check-secrets.ps1` 能阻止明显密钥泄露。
- mock 测试覆盖 StrategySpec、工具调用、报告生成和风险提示。
- 失败样例能稳定失败。

## 推荐推进节奏

先完成 Lab 01 的路由解释和 Lab 02 的 structured trace，再进入 Lab 03 mock 工具调用；随后做 Lab 04-07，把知识检索、偏好记忆和 Skill 固化串起来；最后做 Lab 08-12，接真实数据源、证据报告、模拟组合和评测安全。
