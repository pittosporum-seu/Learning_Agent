# Lab 06: Skill Registry

这个 Lab 展示 `Skill Registry` 的最小教学形态：系统把稳定能力注册成 mock Skill 元数据，再根据 Lab 05 的 Memory + RAG + Evidence 输出选择合适 Skill，或因为安全边界禁用 Skill。

本 Lab 不展示真实 Codex skill runtime，也不使用 `.agents/` 或 `.codex/`。这些目录属于本地运行配置，不进入仓库。这里的 Skill 是本地 mock 元数据，用于学习 Skill Registry、触发条件、禁用条件和人工确认边界。

## Skill 与 Prompt / Tool / Memory 的区别

- Prompt 是一次性的指令或上下文组织方式。
- Tool 是外部能力调用，有入参、返回、失败和权限边界。
- Memory 是受控的上下文资产，用于保留偏好或历史摘要。
- Skill 是稳定流程的能力声明，包含触发场景、输入、输出、禁用场景和人工确认要求。

## 输入

输入包含：

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- 本地 `data/mock_skills.json` 中的 mock Skill 元数据。

Lab 06 会先调用 Lab 05 的 `run_user_preference_memory`，再根据其 `StrategySpec`、`candidate_evidence`、`retrieved_context`、`memory_snapshot` 和 `preference_adjusted_evidence` 构造选择上下文。

## 输出

核心输出是结构化 JSON：

- `memory_output`: Lab 05 的完整输出。
- `registered_skills`: 当前注册的 mock Skills。
- `skill_selection_trace`: 每个 Skill 的触发命中、禁用原因和人工确认状态。
- `selected_skills`: 被选择的 mock Skills。
- `disabled_skills`: 因 blocked、证据不足、缺少风险提示或需要人工确认而禁用的 Skills。
- `requires_human_confirmation`: Skill 元数据中的人工确认字段，高风险交接或执行计划必须为 `true`。
- `final_output`: 选择数量、禁用数量、人工确认项和下一步。
- `risk_disclosure`: 财经输出边界提示。

## Mock Skills

| Skill | 作用 |
| --- | --- |
| `candidate-evidence-summary` | 汇总 mock 候选证据和来源限制。 |
| `negative-news-risk-review` | 复核 mock 风险旗标和风险上下文。 |
| `watchlist-handoff` | 准备观察池交接草稿，必须人工确认。 |
| `simulation-portfolio-plan` | 准备模拟组合计划草稿，必须人工确认。 |

## Demo

运行默认 demo：

```powershell
python labs/06-skill-registry/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 06-skill-registry
```

切换 mock 用户：

```powershell
python labs/06-skill-registry/demo/run_demo.py --user-id balanced_user
```

输出完整 JSON：

```powershell
python labs/06-skill-registry/demo/run_demo.py --json
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 06-skill-registry
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 不做什么

- 不使用 `.agents/` 或 `.codex/` 作为仓库内容。
- 不调用真实模型 API、真实向量数据库或真实财经 API。
- 不生成真实股票推荐、收益承诺、买卖动作或目标价格。
- 不执行自选股、模拟组合或交易动作。
- 不让 blocked 请求选择执行型 Skill。

## 和前后 Lab 的关系

- Lab 05 负责 Memory，把用户偏好转成 adjusted evidence view。
- Lab 06 负责 Skill Registry，把稳定能力声明成可选择、可禁用的 mock Skill。
- Lab 07 会展示如何从稳定流程生成可审查的 Skill 草稿。
