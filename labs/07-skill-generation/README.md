# Lab 07: Skill Generation

这个 Lab 展示 `Skill Generation` 的最小教学形态：系统从 Lab 06 的 mock Skill Registry 输出中，生成一个可审查的 `SKILL.md` 草稿。

本 Lab 不展示真实 Codex Skill runtime，也不使用 `.agents/` 或 `.codex/`。生成结果只是 draft，不自动启用，不写入本地运行配置目录，也不生成投资建议或交易动作。

## Skill Draft 与正式 Skill 的区别

- Skill draft 是候选说明文档，用于人工 review。
- 正式 Skill 是经过人工审核、测试和安全边界确认后，才可能进入某个运行环境的能力包。
- 本 Lab 只生成 draft，并在输出中保留 `draft_review.status=needs_human_review`。

## 为什么不能自动启用

Skill 会影响 Agent 的能力发现、选择和执行边界。即使草稿来自稳定流程，也必须人工确认触发场景、禁用场景、输入输出、风险提示和测试样例。涉及观察池、模拟组合、真实数据源或对外发布的动作，都不能通过自动生成直接启用。

## 输入

输入包含：

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- Lab 06 输出中的 `selected_skills`、`disabled_skills`、`skill_selection_trace` 和上游 evidence。

Lab 07 会先调用 Lab 06 的 `run_skill_registry`，再为最合适的 selected Skill 生成草稿。默认优先选择 `candidate-evidence-summary`。

## 输出

核心输出是结构化 JSON：

- `skill_registry_output`: Lab 06 的完整输出。
- `generated_skill_draft`: 结构化 Skill 草稿。
- `skill_draft_markdown`: 类 `SKILL.md` 的草稿文本，带 `DRAFT` 标记。
- `draft_review`: 安全审查结果，正常路径为 `needs_human_review`。
- `final_output`: 草稿摘要、是否自动启用、是否写 runtime 配置、下一 Lab 指向。
- `risk_disclosure`: 财经输出边界提示。

`generated_skill_draft` 至少包含：

- `name`
- `description`
- `trigger_scenarios`
- `disabled_scenarios`
- `inputs`
- `outputs`
- `workflow_steps`
- `human_confirmation_points`
- `safety_boundaries`
- `test_cases`

## Demo

运行默认 demo：

```powershell
python labs/07-skill-generation/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 07-skill-generation
```

切换 mock 用户：

```powershell
python labs/07-skill-generation/demo/run_demo.py --user-id balanced_user
```

输出完整 JSON：

```powershell
python labs/07-skill-generation/demo/run_demo.py --json
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 07-skill-generation
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 不做什么

- 不使用 `.agents/` 或 `.codex/` 作为仓库内容。
- 不调用真实模型 API、真实向量数据库或真实财经 API。
- 不生成真实股票推荐、收益承诺、交易动作或目标价格。
- 不自动启用生成的 Skill draft。
- 不从 blocked 请求生成可启用 Skill。

## 和前后 Lab 的关系

- Lab 06 负责 Skill Registry，选择或禁用 mock Skill。
- Lab 07 负责 Skill Generation，把被选中的稳定能力生成可审查草稿。
- Lab 08 会进入 MX Skills Adapter，讨论 mock-first 到真实财经 Skills 的受控适配边界。
