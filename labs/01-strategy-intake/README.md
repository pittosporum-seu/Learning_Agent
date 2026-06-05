# Lab 01: Strategy Intake

这个 Lab 解决第一件事：把用户自然语言里的投研想法，解析成结构化 `StrategySpec`。

它对应 `Agent基础知识 01: Workflow vs Agent`。在这个阶段，系统不调用真实模型，不调用真实财经 API，也不输出个股推荐；它只负责把策略意图、筛选条件、风险边界和待确认问题整理清楚。

## 输入

自然语言策略，例如：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。
```

## 输出

结构化 JSON，核心字段包括：

- `market`: 目标市场。
- `themes`: 主题或行业。
- `horizon_days`: 观察时间窗口。
- `candidate_rules`: 候选筛选规则。
- `risk_filters`: 风险过滤规则。
- `user_preferences`: 用户偏好。
- `execution_mode`: `workflow`、`agent` 或 `needs_clarification`。
- `clarification_questions`: 需要用户补充的问题。
- `risk_disclosure`: 固定风险提示。

## 运行

在仓库根目录执行：

```powershell
python labs/01-strategy-intake/src/strategy_intake.py "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。"
```

也可以直接运行默认样例：

```powershell
python labs/01-strategy-intake/src/strategy_intake.py
```

## 测试

```powershell
python -m unittest discover -s labs/01-strategy-intake/tests
```

## 设计边界

- 只做策略解析，不生成个股名单。
- 不接真实 MiMo，也不接东方财富妙想 Skills。
- 缺少主题、时间窗口或筛选规则时，输出待确认问题。
- 发现“稳赚”“必涨”“自动买入”等高风险请求时，转为风险边界提示。
- 所有输出固定包含风险提示。

## 和后续 Lab 的关系

Lab 02 会把 `StrategySpec` 放进 Agent Loop，开始按步骤推进投研流程。

Lab 03 会把 `candidate_rules`、`risk_filters` 映射到 mock 财经工具调用。
