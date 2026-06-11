# Lab 10: Evidence Report 设计

Lab 10 展示 Evidence Report：把 Lab 09 Research Planner DAG 的结构化输出整理成可审查的 mock 证据报告草稿。

本 Lab 仍然是教学展示，不是投资建议系统。报告必须来自 Planner 输出、`adapter_trace`、`candidate_evidence`、`retrieved_context` 和 `planner_trace`；每个关键结论都要能追溯来源，并保留 `risk_disclosure`、`limitations` 和 `human_review_required`。

## 一、教学目标

Lab 10 要让读者看到：证据报告不是模型自由写作，而是把上游结构化证据、状态和限制条件组织成可复核报告。

核心教学目标：

- 报告内容必须来自 Planner 输出、adapter trace、候选证据、RAG 检索片段和 Planner trace。
- 每个候选观察、风险提示、限制条件和状态判断都必须有来源引用。
- 缺少证据时写入 `evidence_gaps`，不能补脑。
- 报告必须保留 `risk_disclosure`、`limitations`、`human_review_required` 和人工确认清单。
- 报告默认是 `draft` 或 `needs_human_review`，不能自动发布、自动加入观察池、自动进入模拟组合或自动交易。

Lab 10 不做：

- 不调用真实模型 API。
- 不调用真实财经 API。
- 不生成投资建议、收益承诺、真实股票推荐或交易动作。
- 不输出买入、卖出、目标价或保证性判断。
- 不把 `preference_adjusted_evidence` 当成原始事实。

## 二、和前面 Lab 的关系

| Lab | 已提供能力 | Lab 10 如何使用 |
| --- | --- | --- |
| Lab 03 Finance Tool Use Mock | `candidate_evidence`、`tool_trace` | 提供候选观察池的原始 mock 证据。 |
| Lab 04 Research RAG Basic | `retrieved_context`、`retrieval_trace` | 提供策略规则、风险规则和报告模板引用片段。 |
| Lab 05 User Preference Memory | `preference_adjusted_evidence`、`memory_trace` | 提供偏好调整后的候选证据视图，但不能覆盖原始证据。 |
| Lab 06 Skill Registry | `selected_skills`、`disabled_skills`、`skill_selection_trace` | 提供可用能力、禁用原因和人工确认边界。 |
| Lab 08 Finance Provider Adapter | `adapter_trace`、`safety_gate` | 提供 provider 调用状态、能力结果和真实 provider 安全门状态。 |
| Lab 09 Research Planner DAG | `research_dag`、`planner_trace`、`waiting_human_confirmation_nodes` | 提供报告生成的运行状态、失败传播、跳过节点和人工确认门。 |
| Lab 10 Evidence Report | draft evidence report | 把上述结构整理成带来源、限制、风险提示和人工确认项的报告草稿。 |

Lab 10 承接 Lab 09 的 `next_lab: Lab 10 Evidence Report`。如果 Lab 09 已经 blocked，Lab 10 只生成 blocked report 和证据缺口说明，不继续正常报告生成。

## 三、报告结构设计

Evidence Report 第一版建议固定为九个 section。每个 section 都是结构化对象，最终可以渲染成 Markdown、JSON 或 web 视图。

### 1. report_header

| 字段 | 说明 |
| --- | --- |
| `report_id` | 报告草稿 ID。 |
| `generated_at` | 报告生成时间。 |
| `source_lab` | 固定来自 `Lab 09 Research Planner DAG`。 |
| `status` | `draft`、`needs_human_review` 或 `blocked`。 |
| `human_review_required` | 是否需要人工复核，默认 true。 |

### 2. strategy_summary

| 字段 | 说明 |
| --- | --- |
| `original_request` | 用户原始自然语言策略。 |
| `themes` | 主题或行业方向。 |
| `horizon_days` | 观察周期。 |
| `routing_mode` | Lab 01 / Lab 09 传入的路由模式。 |
| `output_type` | 用户期望输出，例如观察池、报告草稿或流程计划。 |

### 3. planner_summary

| 字段 | 说明 |
| --- | --- |
| `planner_status` | Lab 09 最终状态。 |
| `completed_nodes` | 已完成节点。 |
| `blocked_nodes` | 已阻断节点及原因。 |
| `skipped_nodes` | 已跳过节点及原因。 |
| `waiting_human_confirmation_nodes` | 等待人工确认节点和确认事项。 |

### 4. candidate_observation_pool

| 字段 | 说明 |
| --- | --- |
| `candidate_id` | mock 候选 ID。 |
| `candidate_name` | mock 候选名称。 |
| `theme` | 主题或方向。 |
| `evidence_refs` | 支撑该观察项的证据引用 ID。 |
| `risk_flags` | 负面资讯、估值观察、流动性等风险旗标。 |
| `preference_status` | 是否被用户偏好保留、过滤或降级展示。 |

### 5. evidence_table

| 字段 | 说明 |
| --- | --- |
| `evidence_id` | 证据 ID。 |
| `source_type` | 来源类型，例如 adapter_trace、candidate_evidence、retrieved_context、planner_trace。 |
| `source_name` | 来源名称、mock 文件或上游字段。 |
| `claim` | 该证据支持的观察或限制。 |
| `value_summary` | 关键数值、摘要或片段。 |
| `limitations` | 数据限制、mock 声明或不确定性。 |
| `confidence` | 证据质量或置信等级。 |

### 6. retrieved_context_table

| 字段 | 说明 |
| --- | --- |
| `source` | 文档来源。 |
| `chunk_id` | 检索片段 ID。 |
| `section` | 文档章节。 |
| `used_for` | 该片段用于报告中的哪个判断。 |
| `matched_terms` | 命中的关键词。 |

### 7. risk_and_limitations

| 字段 | 说明 |
| --- | --- |
| `risk_disclosure` | 财经风险提示，必须存在。 |
| `mock_data_notice` | 说明本报告基于 mock 数据或本地集成摘要。 |
| `evidence_gaps` | 缺失证据、阻断节点或无法验证字段。 |
| `uncertainty_notes` | 不确定性和需要人工复核的问题。 |
| `no_investment_advice` | 明确不构成投资建议或收益承诺。 |

### 8. human_review_checklist

| 字段 | 说明 |
| --- | --- |
| `review_evidence_sources` | 复核证据来源是否完整。 |
| `confirm_no_trading_action` | 确认报告不包含交易动作。 |
| `confirm_risk_disclosure` | 确认风险提示存在且醒目。 |
| `confirm_before_watchlist_simulation_or_publication` | 观察池移交、模拟组合或对外发布前必须人工确认。 |

### 9. next_steps

| 字段 | 说明 |
| --- | --- |
| `next_lab` | 固定为 `Lab 11 Simulation Portfolio`。 |
| `allowed_next_steps` | 允许的下一步，例如人工审阅报告草稿、补齐证据缺口。 |
| `not_allowed_actions` | 禁止动作，例如自动发布、自动加入观察池、自动进入模拟组合或自动交易。 |

## 四、数据契约

以下为文档级结构说明，后续实现时再落成 Python dataclass 或 dict schema。

### EvidenceReport

| 字段 | 说明 |
| --- | --- |
| `report_id` | 报告 ID。 |
| `status` | `draft`、`needs_human_review` 或 `blocked`。 |
| `sections` | `ReportSection` 列表或按 section key 组织的字典。 |
| `evidence_refs` | 报告使用的所有 `EvidenceReference`。 |
| `risk_and_limitations` | `RiskAndLimitation`。 |
| `human_review_checklist` | `HumanReviewChecklist`。 |
| `human_review_required` | 是否必须人工复核。 |

### ReportSection

| 字段 | 说明 |
| --- | --- |
| `section_id` | section 标识，例如 `evidence_table`。 |
| `title` | section 标题。 |
| `status` | section 状态：ready、blocked、degraded。 |
| `content` | section 的结构化内容。 |
| `evidence_refs` | section 直接引用的证据 ID。 |
| `limitations` | section 层面的限制说明。 |

### EvidenceReference

| 字段 | 说明 |
| --- | --- |
| `evidence_id` | 证据 ID。 |
| `source_type` | `adapter_trace`、`candidate_evidence`、`retrieved_context`、`planner_trace` 等。 |
| `source_path` | 上游字段路径或 mock 文件位置。 |
| `source_name` | 可读来源名称。 |
| `claim_supported` | 支撑的报告观察。 |
| `limitations` | 该证据的限制。 |

### CandidateObservation

| 字段 | 说明 |
| --- | --- |
| `candidate_id` | 候选 ID。 |
| `candidate_name` | 候选名称。 |
| `theme` | 候选主题。 |
| `observation_summary` | 证据化观察摘要。 |
| `evidence_refs` | 证据引用 ID 列表。 |
| `risk_flags` | 风险旗标。 |
| `preference_status` | 偏好视图状态。 |

### RiskAndLimitation

| 字段 | 说明 |
| --- | --- |
| `risk_disclosure` | 必须展示的风险提示。 |
| `mock_data_notice` | mock 或本地集成摘要说明。 |
| `evidence_gaps` | 缺失证据。 |
| `uncertainty_notes` | 不确定性说明。 |
| `prohibited_actions` | 禁止动作列表。 |
| `no_investment_advice` | 不构成投资建议的声明。 |

### HumanReviewChecklist

| 字段 | 说明 |
| --- | --- |
| `required` | 是否必需。 |
| `items` | 人工复核项列表。 |
| `blocked_until_reviewed` | 复核前禁止动作。 |
| `review_reason` | 为什么需要人工复核。 |

### ReportGenerationTrace

| 字段 | 说明 |
| --- | --- |
| `step` | 报告生成步骤。 |
| `status` | `completed`、`blocked` 或 `degraded`。 |
| `input_sources` | 使用的上游来源。 |
| `output_section` | 生成或更新的报告 section。 |
| `evidence_refs` | 本步骤新增或使用的证据引用。 |
| `warning_or_gap` | 警告、缺口或阻断原因。 |

## 五、引用和证据规则

Evidence Report 的核心约束是：没有来源，不进报告。

- 报告里的候选、风险、限制和节点状态必须能引用上游字段。
- 允许引用 `adapter_trace`、`candidate_evidence`、`retrieved_context`、`planner_trace`、`research_dag` 和 `waiting_human_confirmation_nodes`。
- 没有来源的内容不能进入 `evidence_table`。
- 缺少证据时写入 `evidence_gaps`，不允许补脑或把模板文字当事实。
- `preference_adjusted_evidence` 只能作为视图调整结果，不能作为原始事实来源。
- 被过滤的候选也可以进入限制说明，但必须标明是偏好或风险规则导致的视图变化。
- `confidence` 表达证据质量，不表达上涨概率、收益概率或交易确定性。

## 六、安全边界

Lab 10 的安全边界必须比普通报告生成更严格，因为它接近用户可读交付物。

禁止字段：

- `buy`
- `sell`
- `recommendation`
- `target_price`

禁止语义：

- 稳赚、必涨、保证收益。
- 自动买入、自动卖出。
- 无来源个股推荐。
- 未经人工确认的观察池移交、模拟组合、Skill 启用或对外发布。

强制要求：

- 报告必须包含 `risk_disclosure`。
- 报告必须包含 `human_review_required=true`。
- 报告默认 `status` 为 `draft` 或 `needs_human_review`。
- blocked planner 输出只能生成 blocked report，不能生成正常候选观察报告。
- 报告必须说明 mock 数据或本地集成摘要的限制。

## 七、Report Generation Trace

`report_generation_trace` 记录报告每个 section 是如何生成的。每条记录至少包含：

- `step`
- `status`
- `input_sources`
- `output_section`
- `evidence_refs`
- `warning_or_gap`

示例形态：

```json
{
  "step": "build_candidate_observation_pool",
  "status": "completed",
  "input_sources": ["candidate_evidence", "preference_adjusted_evidence"],
  "output_section": "candidate_observation_pool",
  "evidence_refs": ["ev-market-001", "ev-news-001"],
  "warning_or_gap": ""
}
```

缺口示例：

```json
{
  "step": "build_evidence_table",
  "status": "degraded",
  "input_sources": ["planner_trace"],
  "output_section": "evidence_table",
  "evidence_refs": [],
  "warning_or_gap": "market_data_check was skipped, so market evidence is missing"
}
```

## 八、Lab 10 输出契约

最终 JSON 输出建议：

| 字段 | 说明 |
| --- | --- |
| `status` | `needs_human_review`、`blocked` 或 `failed`。 |
| `planner_output` | Lab 09 输出摘要或完整 mock 输出。 |
| `evidence_report` | `EvidenceReport`。 |
| `report_generation_trace` | `ReportGenerationTrace` 列表。 |
| `evidence_refs` | 报告引用的所有证据。 |
| `risk_disclosure` | 财经风险提示。 |
| `human_review_required` | 固定为 true，除非 blocked 且无报告可审阅时仍需人工处理。 |
| `final_output` | 报告状态摘要、允许下一步和禁止动作。 |
| `next_lab` | `Lab 11 Simulation Portfolio`。 |

输出边界：

- 可以说明“生成 mock 证据报告草稿，等待人工复核”。
- 可以列出候选观察项和证据引用。
- 不得输出交易动作、目标价、收益承诺或自动执行指令。
- 不得将报告状态直接设为可发布。

## 九、测试设计

Lab 10 实现时至少覆盖这些测试：

- 正常 mock planner 输出能生成 draft report。
- report 必须包含 `risk_disclosure`。
- report status 必须是 `draft` 或 `needs_human_review`。
- 每个 candidate observation 都有 `evidence_refs`。
- `evidence_table` 每条都有 `source_name`、`source_type` 和 `limitations`。
- blocked planner 输出会生成 blocked report，不补脑。
- missing evidence 会进入 `evidence_gaps`。
- 输出不包含 `buy`、`sell`、`recommendation`、`target_price`。
- `human_review_required` 必须为 true。
- `report_generation_trace` 覆盖每个核心 section。
- 不创建 `.agents/` 或 `.codex/`。
- 默认测试不依赖真实 key、真实模型、真实财经 API 或真实 provider 响应。

## 十、后续实现目录规划

Lab 10 实现目录已按本设计创建：

```text
labs/10-evidence-report/
|-- AGENTS.md
|-- README.md
|-- data/
|   `-- report_template.json
|-- src/
|   |-- report_model.py
|   |-- evidence_collector.py
|   |-- report_builder.py
|   |-- report_safety.py
|   `-- run_lab.py
|-- demo/
|   `-- run_demo.py
|-- tests/
`-- outputs/
    `-- .gitkeep
```

当前实现分工：

- `report_model.py` 定义 `EvidenceReport`、`ReportSection`、`EvidenceReference` 和安全字段。
- `evidence_collector.py` 从 Lab 09 输出收集 `adapter_trace`、`candidate_evidence`、`retrieved_context` 和 `planner_trace`。
- `report_builder.py` 生成 report sections 和 `report_generation_trace`。
- `report_safety.py` 检查风险提示、人工确认、禁止字段和缺失证据。
- `run_lab.py` 调用 Lab 09 runner，输出 `evidence_report`、`report_generation_trace` 和 `final_output`。
- README 写清输入、输出、demo、tests、不做什么、和 Lab 09 / Lab 11 的关系。
- AGENTS.md 固化证据引用、报告安全边界和禁止投资建议的规则。
