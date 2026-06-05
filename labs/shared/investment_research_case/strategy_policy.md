# Strategy Policy

这个策略解析规则用于 Lab 01-03。

## 解析目标

把自然语言投研请求整理成 `StrategySpec`，而不是直接给出股票名单。

核心字段：

- `market`: 目标市场，例如 A股、港股、美股。
- `themes`: 主题、行业或板块。
- `horizon_days`: 观察时间窗口。
- `candidate_rules`: 候选筛选规则。
- `risk_filters`: 风险过滤规则。
- `user_preferences`: 用户风险偏好和默认约束。
- `output`: 预期产出。
- `execution_mode`: `workflow`、`agent` 或 `needs_clarification`。

## Workflow 与 Agent 判断

优先使用 Workflow 的情况：

- 条件明确。
- 步骤较少。
- 不依赖多源证据核验。
- 不需要动态规划或人工确认。

需要 Agent 的情况：

- 同时包含趋势、回撤、新闻、公告、财务、报告等多类条件。
- 需要规划多步投研流程。
- 需要聚合多源证据。
- 需要在执行中等待人工确认。

需要追问的情况：

- 缺少目标市场。
- 缺少主题或行业。
- 缺少候选筛选规则。
- 动态条件缺少时间窗口。
- 请求包含高风险交易或收益确定性表述。

## 输出约束

Lab 01 不输出个股名单，不调用真实工具，只输出结构化策略说明和待确认问题。
