# Lab 09: Research Planner DAG 设计

Lab 09 展示 Agent Harness / Planner：把前面 Labs 里已经跑通的策略解析、工具、RAG、Memory、Skill 和 Adapter 能力组织成一个有状态的研究计划 DAG。

本 Lab 仍然是教学展示，不是投资建议系统。默认 mock-first，不调用真实模型 API；默认不调用真实财经 API；若显式透传 Lab 08 的 real provider 手动路径，仅作为本地集成验证，不作为默认教学路径。Lab 09 不生成真实股票推荐，不执行交易动作。任何候选观察池、报告或后续模拟动作都必须保留来源、限制、风险提示和人工确认边界。

## 一、教学目标

Lab 09 要让读者看到：投研 Agent 的 Planner 不是一个线性待办列表，而是一个可观察、可测试、可失败关闭的执行图。

核心教学目标：

- 不再线性调用 Lab 01 到 Lab 08 的模块，而是把任务拆成 DAG 节点。
- 每个节点都有明确的依赖、状态、输入、输出、失败传播和人工确认边界。
- 节点状态可以解释为什么执行、为什么跳过、为什么阻断、为什么等待人工确认。
- Adapter 能力、证据链、Skill 状态和安全边界进入统一计划，而不是散落在最终输出里。
- 默认只使用 mock 数据和上游 mock 输出，真实 provider 只能作为上游 Lab 08 的手动路径，不在 Lab 09 自动启用。

Lab 09 不做：

- 默认不调用真实财经 API；若显式透传 Lab 08 的 real provider 手动路径，仅作为本地集成验证，不作为默认教学路径。
- 不调用真实模型 API。
- 不创建真实自选股、模拟组合或交易动作。
- 不把候选观察池写成投资建议。
- 不绕过 `safety_gate`、`risk_disclosure` 或人工确认节点。

## 二、和前面 Lab 的关系

| Lab | 已提供能力 | Lab 09 如何使用 |
| --- | --- | --- |
| Lab 01 Strategy Intake | `StrategySpec`、`routing_decision` | 作为 DAG 的任务输入和路由依据。 |
| Lab 02 Agent Loop | structured trace、fail closed | 作为 Planner Trace 的设计参照，保留每一步的状态和原因。 |
| Lab 03 Tool Use | `tool_trace`、`candidate_evidence` | 作为候选生成和证据节点的输入来源。 |
| Lab 04 RAG | `retrieved_context`、`retrieval_trace` | 作为证据上下文挂载节点的资料来源。 |
| Lab 05 Memory | `memory_snapshot`、`preference_adjusted_evidence` | 作为偏好调整节点的输入，并限制候选视图。 |
| Lab 06 Skill Registry | `selected_skills`、`disabled_skills`、`skill_selection_trace` | 作为 Skill 选择节点的输入和安全状态来源。 |
| Lab 07 Skill Generation | `generated_skill_draft`、`draft_review` | 作为流程固化状态的参考，但不自动启用 Skill。 |
| Lab 08 Finance Provider Adapter | `adapter_trace`、`safety_gate`、`registered_adapters` | 作为 Adapter 能力检查、候选生成、行情核验和资讯风险核验的上游能力。 |
| Lab 09 Research Planner DAG | Research DAG、节点状态、失败传播、人工确认门 | 把前面能力编排成有状态、可复盘的研究计划。 |

Lab 09 承接 Lab 08 的 `next_lab: Lab 09 Research Planner DAG`。正常路径先读取 Lab 08 输出，再把 `adapter_output` 变成 Planner 的输入上下文。如果 Lab 08 已经 blocked，Lab 09 不应继续正常执行 DAG，而是生成 blocked run state 和失败传播 trace。

## 三、DAG 节点设计

Lab 09 第一版固定生成一张教学型 DAG。后续实现可以根据 `StrategySpec` 调整节点是否启用，但节点语义和安全边界应保持稳定。

| node_id | node_type | depends_on | inputs | outputs | requires_human_confirmation | failure_behavior |
| --- | --- | --- | --- | --- | --- | --- |
| `parse_and_route` | intake | 无 | `request`、Lab 08 上游 `strategy_spec`、`routing_decision` | 标准化 `StrategySpec`、路由状态、禁止动作 | false | 如果路由为 `blocked` 或 `needs_clarification`，下游依赖节点 blocked 或 skipped。 |
| `adapter_capability_check` | safety_check | `parse_and_route` | `registered_adapters`、`adapter_mode`、`provider_mode`、`safety_gate` | 可用 capability、禁用 capability、安全门状态 | false | 如果 `safety_gate.real_provider_allowed=false` 且请求要求真实 provider，阻断 adapter 相关节点；默认 mock 可继续。 |
| `candidate_generation` | adapter_call | `adapter_capability_check` | `StrategySpec`、`candidate-screen` capability、候选规则 | 候选观察池草案、候选生成 trace | false | 上游 blocked 时 skipped；adapter 返回 failed / blocked 时本节点 blocked，并阻断依赖候选的下游。 |
| `market_data_check` | adapter_call | `candidate_generation` | 候选 ID、`market-data` capability | 行情证据、趋势和回撤摘要、数据限制 | false | 候选为空时 skipped；adapter failed 时 blocked，依赖行情的下游只能输出缺口说明。 |
| `news_risk_check` | adapter_call | `candidate_generation` | 候选 ID、`finance-news` capability、风险过滤规则 | 资讯证据、`risk_flags`、负面信息摘要 | false | 候选为空时 skipped；发现高风险旗标时不删除证据，但标记下游需要人工复核。 |
| `evidence_context_attach` | evidence_join | `market_data_check`、`news_risk_check` | `candidate_evidence`、`retrieved_context`、adapter 证据 | 带来源的 `augmented_evidence`、证据缺口 | false | 任一关键证据缺失时 blocked 或 degraded；不得生成无来源断言。 |
| `memory_preference_adjustment` | memory_policy | `evidence_context_attach` | `memory_snapshot`、`effective_user_profile`、`augmented_evidence` | `preference_adjusted_evidence`、偏好应用说明 | false | Memory 只能生成 adjusted view；如果偏好试图覆盖安全边界，记录 ignored 并继续安全路径。 |
| `skill_selection` | skill_policy | `memory_preference_adjustment` | `selected_skills`、`disabled_skills`、`skill_selection_trace`、当前证据状态 | 可用 Skill、禁用原因、需要确认的 Skill | false | 缺风险提示、证据不足或上游 blocked 时禁用执行型 Skill。 |
| `human_review_gate` | human_gate | `skill_selection` | 风险提示、候选观察池、Skill 状态、证据缺口、安全门状态 | 待人工确认事项、确认前禁止动作 | true | 不自动 completed。正常路径进入 `waiting_human_confirmation`；缺 `risk_disclosure` 时 blocked。 |

### 关键依赖

- `candidate_generation`、`market_data_check`、`news_risk_check` 都依赖 `adapter_capability_check`。
- `market_data_check` 和 `news_risk_check` 可以在候选生成后并行执行。
- `evidence_context_attach` 必须等待行情和资讯风险节点有明确状态。
- `memory_preference_adjustment` 只能调整证据视图，不能修改原始 evidence。
- `skill_selection` 必须看见证据状态和风险提示，不能只看用户请求。
- `human_review_gate` 是所有候选观察池、报告交付、模拟组合或 Skill 启用之前的边界。

## 四、节点状态设计

| 状态 | 出现条件 | 说明 |
| --- | --- | --- |
| `pending` | DAG 已构建，但依赖尚未满足。 | 初始状态。 |
| `ready` | 所有必需依赖已 completed，且没有阻断信号。 | 可以进入执行队列。 |
| `running` | 节点正在执行。 | 只在 executor 运行期间出现。 |
| `completed` | 节点正常产出结构化结果。 | 结果必须写入 `produced_outputs`。 |
| `blocked` | 节点因安全、缺信息、上游失败或关键输出缺失停止。 | 必须给出 `blocked_reason`。 |
| `skipped` | 节点因为依赖节点 blocked / skipped 或条件不适用而跳过。 | 必须给出 `skipped_reason`，不能静默跳过。 |
| `waiting_human_confirmation` | 节点正常执行到人工确认边界。 | `human_review_gate` 的正常终态，不自动 completed。 |

推荐状态流转：

```text
pending -> ready -> running -> completed
pending -> skipped
ready -> running -> blocked
running -> waiting_human_confirmation
```

不允许的流转：

- `blocked` 自动回到 `completed`。
- `waiting_human_confirmation` 自动变成 `completed`。
- 下游节点在必需依赖 blocked 时继续正常 completed。

## 五、失败传播规则

Planner 必须 fail closed，失败传播规则优先于生成完整报告的欲望。

1. 上游节点 `blocked` 时，依赖它的下游节点必须 `skipped` 或 `blocked`。
2. 上游节点 `skipped` 时，下游如果没有替代输入，也必须 `skipped`。
3. `parse_and_route` 返回 `blocked` 时，所有 adapter、evidence、memory、skill 和 human gate 节点都不得正常执行。
4. `adapter_capability_check` 发现外部 provider safety gate 不通过，且请求要求真实 provider 时，`candidate_generation`、`market_data_check`、`news_risk_check` 不继续正常执行。
5. 默认 mock adapter 可用时，真实 provider safety gate 不通过不应阻断 mock 路径，但必须在 planner trace 中记录。
6. `candidate_generation` 无候选时，`market_data_check`、`news_risk_check` 可以 `skipped`，`evidence_context_attach` 必须输出证据缺口。
7. 缺少 `risk_disclosure` 时，`human_review_gate` 必须 `blocked`。
8. `human_review_gate` 的正常终态是 `waiting_human_confirmation`，不能自动 `completed`。
9. `skill_selection` 发现需要人工确认的 Skill 时，不能把它标记成可自动执行。
10. 任何节点发现输出包含 `buy`、`sell`、`recommendation`、`target_price` 这类禁止字段时，Planner run 必须 blocked。

## 六、数据契约

以下是文档级结构说明，后续实现时再落成 Python dataclass 或 dict schema。

### ResearchDagNode

| 字段 | 说明 |
| --- | --- |
| `node_id` | 节点唯一标识，例如 `candidate_generation`。 |
| `node_type` | 节点类型，例如 intake、adapter_call、evidence_join、human_gate。 |
| `depends_on` | 依赖节点列表。 |
| `status` | 当前状态：pending、ready、running、completed、blocked、skipped、waiting_human_confirmation。 |
| `inputs` | 节点需要读取的上游字段名或摘要。 |
| `outputs` | 节点产出的字段名或摘要。 |
| `requires_human_confirmation` | 是否需要人工确认。 |
| `failure_behavior` | 失败时如何传播。 |
| `blocked_reason` | blocked 时的原因。 |
| `skipped_reason` | skipped 时的原因。 |

### PlannerTraceEvent

| 字段 | 说明 |
| --- | --- |
| `event_id` | trace 事件编号。 |
| `node_id` | 关联节点。 |
| `status` | 本次事件后的节点状态。 |
| `reason` | 状态变化原因。 |
| `dependency_status` | 依赖节点状态快照。 |
| `started_from` | 节点从哪个状态进入当前动作。 |
| `produced_outputs` | 本次动作生成的关键输出摘要。 |
| `blocked_reason` | 阻断原因。 |
| `skipped_reason` | 跳过原因。 |

### PlannerRunState

| 字段 | 说明 |
| --- | --- |
| `run_id` | 一次 Planner 运行的标识。 |
| `status` | completed、blocked、waiting_human_confirmation 或 failed。 |
| `request` | 用户原始请求。 |
| `adapter_output` | Lab 08 输出摘要或完整 mock 输出。 |
| `research_dag` | `ResearchDagNode` 列表。 |
| `planner_trace` | `PlannerTraceEvent` 列表。 |
| `blocked_nodes` | 所有 blocked 节点。 |
| `skipped_nodes` | 所有 skipped 节点。 |
| `waiting_human_confirmation_nodes` | 等待人工确认的节点。 |
| `risk_disclosure` | 必须保留的风险提示。 |

### HumanReviewGate

| 字段 | 说明 |
| --- | --- |
| `gate_id` | 人工确认门编号。 |
| `node_id` | 通常为 `human_review_gate`。 |
| `required_confirmations` | 需要人工确认的事项，例如发布报告、加入观察池、启用 Skill。 |
| `blocked_until_confirmed` | 确认前禁止继续的动作。 |
| `risk_disclosure_present` | 是否存在风险提示。 |
| `evidence_gaps` | 需要人工复核的证据缺口。 |
| `safety_notes` | 安全边界说明。 |
| `status` | waiting_human_confirmation 或 blocked。 |

### PlannerFinalOutput

| 字段 | 说明 |
| --- | --- |
| `summary` | Planner 运行摘要。 |
| `completed_nodes` | 已完成节点 ID。 |
| `blocked_nodes` | 已阻断节点 ID 和原因。 |
| `waiting_human_confirmation_nodes` | 等待人工确认节点 ID 和事项。 |
| `evidence_summary` | 证据摘要和缺口，不包含投资建议。 |
| `allowed_next_steps` | 安全允许的下一步，例如进入 Lab 10 Evidence Report 的 mock 报告草稿。 |
| `prohibited_actions` | 禁止动作，例如自动交易、无确认发布、无证据推荐。 |
| `next_lab` | 固定为 `Lab 10 Evidence Report`。 |

## 七、Planner Trace

`planner_trace` 让读者看到 Planner 的每个节点为什么变成当前状态。每条记录至少包含：

- `node_id`
- `status`
- `reason`
- `dependency_status`
- `started_from`
- `produced_outputs`
- `blocked_reason` 或 `skipped_reason`

示例形态：

```json
{
  "node_id": "market_data_check",
  "status": "completed",
  "reason": "candidate_generation completed and market-data capability is available",
  "dependency_status": {
    "candidate_generation": "completed"
  },
  "started_from": "ready",
  "produced_outputs": {
    "market_evidence_count": 2,
    "source": "mock-finance adapter"
  },
  "blocked_reason": "",
  "skipped_reason": ""
}
```

阻断示例：

```json
{
  "node_id": "human_review_gate",
  "status": "blocked",
  "reason": "risk disclosure is missing",
  "dependency_status": {
    "skill_selection": "completed"
  },
  "started_from": "ready",
  "produced_outputs": {},
  "blocked_reason": "missing risk_disclosure",
  "skipped_reason": ""
}
```

## 八、Lab 09 输出契约

最终 JSON 输出建议：

| 字段 | 说明 |
| --- | --- |
| `status` | Planner 运行状态。正常教学路径通常为 `waiting_human_confirmation`，高风险或缺信息为 `blocked`。 |
| `adapter_output` | Lab 08 输出摘要，至少包含 `adapter_trace`、`safety_gate`、`provider_mode`、`risk_disclosure`。 |
| `research_dag` | `ResearchDagNode` 列表。 |
| `planner_trace` | `PlannerTraceEvent` 列表。 |
| `blocked_nodes` | 阻断节点及原因。 |
| `waiting_human_confirmation_nodes` | 等待人工确认节点及确认事项。 |
| `final_output` | `PlannerFinalOutput`。 |
| `risk_disclosure` | 财经风险提示。 |
| `next_lab` | `Lab 10 Evidence Report`。 |

输出边界：

- 可以说明“候选观察池证据准备完成，等待人工确认进入报告草稿”。
- 不得输出买入、卖出、目标价、收益承诺或自动交易动作。
- 不得因为 Memory 偏好而删除原始 evidence 来源。
- 不得因为 Skill 被选中而自动启用 Skill 或绕过人工 review。

## 九、测试设计

Lab 09 实现时至少覆盖这些测试：

- DAG 模型能校验依赖，缺失依赖会失败。
- builder 能生成所有 required nodes。
- executor 能按依赖顺序执行。
- `market_data_check` 和 `news_risk_check` 在候选生成后可以独立完成。
- 上游 blocked 时下游 skipped / blocked。
- adapter safety gate 不通过时，真实 provider 路径不会继续执行。
- `human_review_gate` 必须进入 `waiting_human_confirmation`，不能自动 completed。
- 缺少 `risk_disclosure` 时 `human_review_gate` blocked。
- `planner_trace` 包含每个节点的 `status` 和 `reason`。
- 输出包含 `risk_disclosure`。
- 输出不包含 `buy`、`sell`、`recommendation`、`target_price`。
- 不创建 `.agents/` 或 `.codex/`。
- 默认测试不依赖真实 key、真实模型、真实财经 API 或真实 provider 响应；显式透传 Lab 08 的 real provider 手动路径仅用于本地集成验证，不作为默认教学路径。

## 十、后续实现目录规划

本轮只新增设计文档，不创建 Lab 目录。下一步实现 Lab 09 时再创建：

```text
labs/09-research-planner/
|-- AGENTS.md
|-- README.md
|-- data/
|   `-- planner_template.json
|-- src/
|   |-- dag_model.py
|   |-- planner_builder.py
|   |-- planner_executor.py
|   `-- run_lab.py
|-- demo/
|   `-- run_demo.py
|-- tests/
`-- outputs/
    `-- .gitkeep
```

后续实现建议：

- `dag_model.py` 定义 `ResearchDagNode` 和依赖校验。
- `planner_builder.py` 根据 Lab 08 输出构建固定教学 DAG。
- `planner_executor.py` 执行状态流转、失败传播和人工确认门。
- `run_lab.py` 调用 Lab 08 runner，输出 `research_dag`、`planner_trace` 和 `PlannerFinalOutput`。
- README 写清输入、输出、demo、tests、不做什么、和 Lab 08 / Lab 10 的关系。
- AGENTS.md 固化 mock-first、fail closed、人工确认和禁止投资建议的规则。
