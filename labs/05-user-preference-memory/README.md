# Lab 05: User Preference Memory

这个 Lab 展示 `Memory` 的最小教学形态：系统读取本地 mock 用户偏好和 memory events，把风险偏好、候选数量、排除主题、排除风险旗标和报告风格转成 `effective_user_profile`，再影响候选证据的展示视图。

Memory 在这里不是长期真实用户画像系统。它只用于演示偏好如何进入 Agent 上下文，并且不能覆盖证据、不能删除来源、不能绕过安全边界、不能生成投资建议。

## 输入

输入包含两部分：

- 自然语言投研策略，例如：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

- mock `user_id`，默认是 `conservative_user`。

内置两个 mock profile：

| user_id | 说明 |
| --- | --- |
| `conservative_user` | 低风险偏好，最多 1 个候选，排除 `negative_news` 和 `valuation_watch`。 |
| `balanced_user` | 中等风险偏好，最多 2 个候选，排除 `negative_news`。 |

## 输出

核心输出是结构化 JSON：

- `memory_snapshot`: 本地 mock profile 和 memory events 的快照。
- `memory_trace`: 读取 Memory、生成有效偏好、应用偏好的过程。
- `effective_user_profile`: 可传给上游策略解析的偏好视图。
- `rag_output`: Lab 04 的 RAG 输出，保留原始 `candidate_evidence`。
- `preference_application`: 已应用、已忽略和安全提示。
- `preference_adjusted_evidence`: 受偏好影响的候选证据视图。
- `final_output`: 调整前后数量、报告风格、下一步和风险提示。
- `risk_disclosure`: 财经输出边界提示。

## Memory 与证据的关系

- Memory 可以影响候选证据视图，但不修改原始 `rag_output.candidate_evidence`。
- Memory 可以过滤 adjusted view 中的主题或风险旗标，但不能删除来源字段。
- Memory 可以选择 `report_style`，但不能把偏好写成投资结论。
- Memory 不能覆盖 `risk_disclosure`，不能跳过 guardrails，也不能授权交易。
- 上游 Lab 04 如果 blocked，本 Lab 也 blocked，不继续正常偏好应用。

## Demo

运行默认 demo：

```powershell
python labs/05-user-preference-memory/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 05-user-preference-memory
```

切换 mock 用户：

```powershell
python labs/05-user-preference-memory/demo/run_demo.py --user-id balanced_user
```

输出完整 JSON：

```powershell
python labs/05-user-preference-memory/demo/run_demo.py --json
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 05-user-preference-memory
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 不做什么

- 不保存真实用户隐私或账户信息。
- 不接真实长期记忆存储。
- 不调用真实模型 API、真实向量数据库或真实财经 API。
- 不生成真实股票推荐、收益承诺、买卖动作或目标价格。
- 不让 Memory 覆盖证据、来源、风险提示或人工确认边界。

## 和前后 Lab 的关系

- Lab 04 负责 RAG，把本地规则和模板片段接入候选证据。
- Lab 05 负责 Memory，把用户偏好转成受控的 adjusted evidence view。
- Lab 06 会进入 Skill Registry，把稳定能力注册为可选择、可审查的 Skill。
