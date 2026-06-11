# Lab 09: Research Planner DAG

这个 Lab 展示 `Research Planner DAG` / `Agent Harness`：把 Lab 08 的 Finance Provider Adapter 输出组织成一个有状态、有依赖、有失败传播和人工确认边界的研究计划 DAG。

投研仍然只是教学场景。本 Lab 不调用真实模型 API、不调用真实向量数据库；默认不调用真实财经 API；若显式透传 Lab 08 的 real provider 手动路径，仅作为本地集成验证，不作为默认教学路径。本 Lab 不生成投资建议、真实股票推荐、收益承诺或交易动作。

## 展示什么

线性 plan 通常只是步骤列表，例如先生成候选、再查行情、再查资讯。DAG 则要求每个节点显式声明：

- `node_id`
- `node_type`
- `depends_on`
- `status`
- `inputs`
- `outputs`
- `requires_human_confirmation`
- `failure_behavior`

Lab 09 用固定教学模板展示这些节点如何按依赖流转：

1. `parse_and_route`
2. `adapter_capability_check`
3. `candidate_generation`
4. `market_data_check`
5. `news_risk_check`
6. `evidence_context_attach`
7. `memory_preference_adjustment`
8. `skill_selection`
9. `human_review_gate`

正常 mock 路径不会把整体状态设为 `completed`，而是停在 `waiting_human_confirmation`。这表示系统已经准备好进入 Lab 10 的证据报告草稿，但在报告发布、观察池移交、模拟组合或 Skill 启用之前，必须有人类确认。

## 输入

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- `adapter_mode`，默认 `mock-finance`。
- 可选 adapter capability 列表，默认 `candidate-screen,market-data,finance-news`。

Lab 09 会调用 Lab 08 的 `run_finance_provider_adapter`，然后只消费其结构化输出，不在本 Lab 再次执行 adapter 或外部 provider。

## 输出

核心输出是结构化 JSON：

- `status`: `waiting_human_confirmation`、`blocked` 或 `completed`。
- `adapter_output`: Lab 08 输出。
- `research_dag`: DAG 节点列表。
- `planner_trace`: 每个节点的状态、原因、依赖状态和产出摘要。
- `blocked_nodes`: 被阻断节点。
- `skipped_nodes`: 因依赖失败或不适用而跳过的节点。
- `waiting_human_confirmation_nodes`: 等待人工确认的节点。
- `final_output`: Planner 摘要和可进入下一 Lab 的安全下一步。
- `risk_disclosure`: 财经风险提示。
- `next_lab`: `Lab 10 Evidence Report`。

`planner_trace` 每条记录至少包含：

- `node_id`
- `status`
- `reason`
- `dependency_status`
- `started_from`
- `produced_outputs`
- `blocked_reason`
- `skipped_reason`

## Demo

运行默认 mock demo：

```powershell
python labs/09-research-planner/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 09-research-planner
```

查看完整 JSON：

```powershell
python labs/09-research-planner/demo/run_demo.py --json
```

查看 blocked 路径：

```powershell
python labs/09-research-planner/demo/run_demo.py --request "直接告诉我明天必涨的股票并自动买入。"
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 09-research-planner
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

测试覆盖：

- DAG 依赖校验、缺失依赖和循环依赖。
- builder 生成所有 required nodes。
- 正常 mock 路径从 `parse_and_route` 到 `skill_selection` 都 completed。
- `human_review_gate` 正常进入 `waiting_human_confirmation`，不能自动 completed。
- 上游 blocked 时下游 skipped / blocked。
- 缺少 `risk_disclosure` 时 `human_review_gate` blocked。
- `planner_trace` 包含每个节点的 `status` 和 `reason`。
- 输出包含 `risk_disclosure`，且不包含禁止输出字段。
- 不创建 `.agents/` 或 `.codex/`。

## 不做什么

- 不调用真实模型 API。
- 不调用真实向量数据库。
- 默认不调用真实财经 API；若显式透传 Lab 08 的 real provider 手动路径，仅作为本地集成验证，不作为默认教学路径。
- 不保存真实用户隐私或真实 provider response。
- 不生成投资建议、收益承诺、真实股票推荐或交易动作。
- 不自动通过人工确认。

## 和前后 Lab 的关系

- Lab 08 负责 Finance Provider Adapter，输出 `adapter_trace` 和 `safety_gate`。
- Lab 09 负责 Research Planner DAG，把 adapter、证据、Memory、Skill 和安全边界编排成有状态执行图。
- Lab 10 将基于 Planner 输出生成 Evidence Report 草稿，继续保留来源、限制和人工确认边界。
