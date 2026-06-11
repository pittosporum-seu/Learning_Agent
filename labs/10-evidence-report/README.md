# Lab 10: Evidence Report

这个 Lab 展示 `Evidence Report`：把 Lab 09 的 Research Planner DAG 输出整理成一个可审查的 mock 证据报告草稿。

投研仍然只是教学场景。本 Lab 不调用真实模型 API、不调用真实向量数据库、不调用真实财经 API，不生成投资建议、真实股票推荐、收益承诺、目标价或交易动作。

## 展示什么

Lab 10 的重点不是让模型写一篇看起来完整的报告，而是展示报告如何从结构化证据生成：

- `planner_output`
- `adapter_trace`
- `candidate_evidence`
- `retrieved_context`
- `planner_trace`

报告固定输出 9 个 section：

1. `report_header`
2. `strategy_summary`
3. `planner_summary`
4. `candidate_observation_pool`
5. `evidence_table`
6. `retrieved_context_table`
7. `risk_and_limitations`
8. `human_review_checklist`
9. `next_steps`

正常 mock 路径的报告状态是 `needs_human_review`，因为 Lab 09 停在 `human_review_gate`。blocked 路径只生成 blocked report 和 `evidence_gaps`，不会补出正常候选观察。

## 输入

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- `adapter_mode`，默认 `mock-finance`。
- 可选 adapter capability 列表，默认 `candidate-screen,market-data,finance-news`。

Lab 10 会调用 Lab 09 的 `run_research_planner_dag`，然后只消费其结构化输出，不在本 Lab 调用真实 provider 或外部服务。

## 输出

核心输出是结构化 JSON：

- `status`: `needs_human_review`、`blocked` 或 `failed`。
- `planner_output`: Lab 09 输出摘要。
- `evidence_report`: 报告主体，包含 9 个 section。
- `report_generation_trace`: 每个 section 的生成步骤、输入来源、证据引用和缺口。
- `evidence_refs`: 报告引用的所有证据。
- `risk_disclosure`: 财经风险提示。
- `human_review_required`: 固定为 true。
- `report_safety_review`: 风险提示、人工确认和禁止字段检查结果。
- `final_output`: 报告摘要、安全下一步和禁止动作。
- `next_lab`: `Lab 11 Simulation Portfolio`。

## Demo

运行默认 mock demo：

```powershell
python labs/10-evidence-report/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 10-evidence-report
```

查看完整 JSON：

```powershell
python labs/10-evidence-report/demo/run_demo.py --json
```

查看 blocked 路径：

```powershell
python labs/10-evidence-report/demo/run_demo.py --request "直接告诉我明天必涨的股票并自动买入。"
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 10-evidence-report
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

测试覆盖：

- 正常 mock planner 输出生成 `needs_human_review` report。
- report 必须包含 `risk_disclosure`。
- 每个 candidate observation 都有 `evidence_refs`。
- `evidence_table` 每条都有 `source_name`、`source_type` 和 `limitations`。
- blocked planner 输出生成 blocked report，不补正常候选观察。
- missing evidence 进入 `evidence_gaps`。
- 输出不包含禁止输出字段。
- `human_review_required` 必须为 true。
- `report_generation_trace` 覆盖每个核心 section。
- 不创建 `.agents/` 或 `.codex/`。

## 不做什么

- 不调用真实模型 API、真实向量数据库或真实财经 API。
- 不保存真实用户隐私或真实 provider response。
- 不生成投资建议、收益承诺、真实股票推荐、目标价或交易动作。
- 不自动加入观察池、自选股或模拟组合。
- 不自动通过人工确认。

## 和前后 Lab 的关系

- Lab 09 负责 Research Planner DAG，输出 `research_dag`、`planner_trace`、`blocked_nodes`、`skipped_nodes` 和 `waiting_human_confirmation_nodes`。
- Lab 10 负责 Evidence Report，把 Planner 输出整理成可复核报告草稿。
- Lab 11 将在人工确认边界之后设计 Simulation Portfolio，但仍保持 mock-first 和人工确认。
