# 个性化投研 Agent Lab 总计划

这组 Lab 用一个连续场景贯穿 12 篇 `Agent基础知识`：构建一个个性化投资调研系统。每个 Lab 都应该能独立运行，但它们共同拼成一个从自然语言策略到证据化报告、Skill 固化和模拟验证的系统。

## 共享案例

所有 Lab 统一围绕这个案例展开：

```text
用户希望根据自己的自然语言策略，生成投研流程规划，筛出候选股票，补充行情、财务、资讯证据，形成观察池；当流程稳定后，沉淀成可复用 Skill。
```

默认示例策略：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。
```

共享材料规划放在 `labs/shared/investment_research_case/`：

- `strategy_request.md`: 用户策略样例。
- `strategy_policy.md`: 策略解析和风险边界。
- `risk_policy.md`: 输出风险提示和禁用场景。
- `user_profile.md`: 用户偏好、风险承受能力、排除条件。
- `mock_universe.csv`: mock 股票池。
- `mock_prices.csv`: mock 行情数据。
- `mock_news.md`: mock 新闻、公告、研报摘要。
- `report_template.md`: 证据化报告模板。

## Lab 路线

| Lab | 名称 | 对应文章 | 目标产出 |
| --- | --- | --- | --- |
| 01 | Strategy Intake | 01 Workflow vs Agent | 自然语言策略转 `StrategySpec` |
| 02 | Strategy Agent Loop | 02 Agent Loop | 用循环执行策略理解、计划和下一步选择 |
| 03 | Finance Tool Use Mock | 03 Tool Use | 用 mock 工具模拟 `mx-xuangu`、`mx-data`、`mx-search` |
| 04 | Research RAG Basic | 04 RAG | 检索策略规则、风险规则和投研模板 |
| 05 | User Preference Memory | 05 Memory | 记住用户风险偏好、排除行业、候选数量 |
| 06 | Skill Registry | 06 MCP / 10 Skills | 建立 Skill 注册表和能力选择机制 |
| 07 | Skill Generation | 10 Skills | 把稳定投研流程生成 `SKILL.md` 草稿 |
| 08 | MX Skills Adapter | 03 Tool Use / 06 MCP | 默认 mock，有 `MX_APIKEY` 时接真实妙想 Skills |
| 09 | Research Planner | 07 Agent Harness | 生成投研 DAG 并管理步骤状态 |
| 10 | Evidence Report | 04 RAG / 12 Evaluation | 生成带来源、时间、证据和风险提示的报告 |
| 11 | Simulation Portfolio | 11 Browser / Computer Use Agent / Safety | 用 mock 或 `mx-moni` 风格接口做模拟组合验证 |
| 12 | Evaluation & Safety | 12 Evaluation / Trace / Safety | 检查密钥泄露、无证据推荐、风险提示缺失等问题 |

## 每个 Lab 的统一结构

每个 Lab 目录建议包含：

```text
README.md
demo/
src/
tests/
data/
outputs/
```

`README.md` 固定写清楚：

- 本 Lab 解决什么问题。
- 输入是什么。
- 输出是什么。
- 如何运行 mock 版本。
- 如何运行 demo。
- 如何切换真实数据源。
- 哪些操作需要人工确认。
- 验收标准是什么。

## Lab 01: Strategy Intake

状态：已实现第一版 mock 解析器和 demo，见 `labs/01-strategy-intake/`。

目标：把用户自然语言策略解析成结构化 `StrategySpec`。

关键点：

- 先判断这是固定 Workflow 还是需要 Agent。
- 把模糊条件拆成市场、主题、时间窗口、候选规则、风险过滤、输出要求。
- 不在这一层调用真实财经数据。

验收标准：

- 给定策略文本，可以输出稳定 JSON。
- 缺少关键字段时能提出待确认问题。
- 输出中不出现股票推荐结论。
- 可以通过 `scripts/run-lab-demo.ps1` 运行 demo，通过 `scripts/run-lab-tests.ps1` 跑回归测试。

## Lab 02: Strategy Agent Loop

目标：让系统具备最小 Agent Loop：观察当前状态、选择下一步、执行一步、记录结果。

关键点：

- 每一轮只做一个清晰动作。
- 状态里保留 `StrategySpec`、待办步骤、已完成步骤和错误。
- 失败时能回退到人工确认或重新规划。

验收标准：

- mock 运行能完成一条策略的计划生成。
- 日志可追踪每一步为什么发生。

## Lab 03: Finance Tool Use Mock

目标：在不接真实 API 的情况下，把财经工具调用模式跑通。

关键点：

- `select_candidates()` 模拟 `mx-xuangu`。
- `fetch_market_data()` 模拟 `mx-data`。
- `search_finance_news()` 模拟 `mx-search`。
- 工具返回结构化数据，不直接写最终结论。

验收标准：

- 工具入参、出参稳定。
- 工具失败能被 Agent 捕获。
- 测试不依赖真实 API Key。

## Lab 04: Research RAG Basic

目标：让系统能从策略规则、风险规则、报告模板中检索相关片段。

关键点：

- 先用本地文本和简单检索实现，不急着引入复杂向量库。
- 报告必须引用检索到的规则。
- 当资料不足时输出“证据不足”，而不是补脑。

验收标准：

- 报告能列出引用来源。
- 风险规则能被检索并参与输出。

## Lab 05: User Preference Memory

目标：让系统记住用户偏好，但不把偏好当成投资结论。

关键点：

- 记录风险等级、排除条件、候选数量、关注主题。
- 区分短期上下文和长期偏好。
- 提供重置和覆盖机制。

验收标准：

- 同一策略在不同用户偏好下输出不同筛选计划。
- 记忆内容可解释、可查看、可清除。

## Lab 06: Skill Registry

目标：建立可复用 Skill 的注册表，让系统知道什么时候调用哪个能力。

关键点：

- Skill 元数据包含名称、触发条件、输入、输出、禁用场景。
- 投研系统先注册 mock Skill，再映射到东方财富妙想 Skills。
- 不把所有事情都塞进一个大 Prompt。

验收标准：

- 系统能根据任务选择合适 Skill。
- 禁用场景能阻止不合适调用。

## Lab 07: Skill Generation

目标：把稳定投研流程生成 `SKILL.md` 草稿。

关键点：

- 从执行轨迹中提取稳定步骤。
- 写清楚触发场景、禁用场景、风险边界和输出格式。
- 新 Skill 生成后进入审核，不自动启用。

验收标准：

- 能从一次完整投研流程生成 Skill 草稿。
- 草稿包含风险提示和测试样例。

## Lab 08: MX Skills Adapter

目标：把 mock 工具和真实东方财富妙想 Skills 放到同一个适配层下。

关键点：

- 默认使用 mock。
- 检测到 `MX_APIKEY` 后才允许启用真实数据源。
- `mx-moni` 只进入模拟组合验证流程，不能绕过人工确认。

验收标准：

- 无密钥时测试仍能通过。
- 有密钥时可切换真实数据源。
- 输出中记录数据来源和查询时间。

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

先完成 Lab 01-03，跑通“策略解析、Agent Loop、mock 工具调用”；再做 Lab 04-07，把知识检索、偏好记忆和 Skill 固化串起来；最后做 Lab 08-12，接真实数据源、证据报告、模拟组合和评测安全。
