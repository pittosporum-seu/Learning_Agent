# Lab 03: Finance Tool Use Mock

这个 Lab 展示 `Tool Use`：Agent 如何从结构化策略出发，选择工具、组织入参、接收工具返回、处理工具失败，并把工具结果转成 `candidate_evidence`。

本 Lab 不调用真实财经 API，不调用真实模型 API，不生成真实股票推荐。所有数据都来自本目录下的 mock 文件，输出只是学习用的 mock 观察池证据。

## 输入

输入是一段自然语言投研策略，例如：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

Lab 03 会复用 Lab 01 的 `parse_strategy_request` 得到 `StrategySpec`。如果 `routing_decision.mode` 是 `blocked` 或 `needs_clarification`，系统会停止，不会调用任何工具。

## 输出

核心输出是结构化 JSON：

- `strategy_spec`: Lab 01 解析出的策略对象。
- `registered_tools`: 当前注册的 mock 工具。
- `tool_trace`: 每次工具选择、入参、返回摘要和失败状态。
- `candidate_evidence`: 工具结果转成的结构化证据。
- `final_output`: 证据数量、风险旗标、下一步 Lab 和风险提示。
- `risk_disclosure`: 财经输出边界说明。

`candidate_evidence` 只说明 mock 候选为什么进入观察池证据，不包含 `buy`、`sell`、`recommendation` 或 `target_price` 字段。

## Mock Tools

| 工具 | 模拟能力 | 数据来源 |
| --- | --- | --- |
| `select_candidates` | 按主题、筛选规则和风险过滤选择 mock 候选 | `data/mock_universe.csv` |
| `fetch_market_data` | 返回 `trend_score`、`max_drawdown`、`turnover_level`、`valuation_note` | `data/mock_prices.csv` |
| `search_finance_news` | 返回 mock 新闻片段和 `risk_flags` | `data/mock_news.md` |

## Demo

运行内置 demo：

```powershell
python labs/03-finance-tool-use-mock/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 03-finance-tool-use-mock
```

传入自定义请求：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 03-finance-tool-use-mock -Request "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
```

输出完整 JSON：

```powershell
python labs/03-finance-tool-use-mock/demo/run_demo.py --json
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 03-finance-tool-use-mock
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 不做什么

- 不查真实行情。
- 不查真实新闻。
- 不调用真实东方财富妙想 Skills。
- 不调用真实模型 API。
- 不生成真实股票推荐。
- 不输出买卖动作、目标价、收益承诺或自动交易指令。

## 和前后 Lab 的关系

- Lab 02 生成的是 mock 投研计划和 structured trace，其中 `mock_tool` 还只是占位。
- Lab 03 把这些占位具体化成可注册、可调用、可追踪的本地 mock 工具。
- Lab 04 会在 Lab 03 的 `candidate_evidence` 基础上引入 RAG，把资料片段、规则和报告模板纳入证据链。
