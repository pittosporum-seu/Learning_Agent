# Lab 08: MX Skills Adapter

这个 Lab 展示 `Adapter` 的最小教学形态：把 Lab 03 的 mock finance tools 和未来真实东方财富妙想 Skills 放到统一 adapter contract 下。

本 Lab 第一版只实现 mock adapter 和 real adapter stub。默认只使用 `mock-mx`，`real-mx-stub` 不读取真实 key、不发送网络请求，调用时会被 `safety_gate` 阻断。它不使用 `.agents/` 或 `.codex/`，也不生成投资建议或交易动作。

## Adapter 与 Tool / Skill / MCP 的区别

- Tool 是单个可调用能力，例如候选筛选、行情查询、资讯搜索。
- Skill 是稳定流程的能力声明，描述何时使用、如何使用和何时禁用。
- MCP 是一种把外部工具暴露给模型或 Agent 的协议生态。
- Adapter 是工程边界层，把不同 provider 的能力统一成同一个 contract，并把 mock-first、安全门和错误处理放在一处。

## 为什么第一版不接真实东方财富妙想 Skills

真实 provider 会涉及密钥、认证响应、数据权限、成本、时效性和人工确认。为了让学习路径稳定可跑，本 Lab 只展示适配形状：真实 provider 必须等未来明确人工确认、环境变量、手动集成测试和响应脱敏策略之后才能启用。

## 输入

输入包含：

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- adapter mode，默认 `mock-mx`。
- Lab 07 输出中的 Skill draft 和上游证据。

Lab 08 会先调用 Lab 07 的 `run_skill_generation`。如果上游 blocked，本 Lab 也 blocked，不调用 adapter。

## 输出

核心输出是结构化 JSON：

- `skill_generation_output`: Lab 07 的完整输出。
- `registered_adapters`: 当前注册的 mock adapter 和 real stub。
- `adapter_mode`: 当前 adapter，默认 `mock-mx`。
- `adapter_trace`: 每次 adapter 调用的 `AdapterResult`。
- `safety_gate`: 真实 provider 是否允许、为什么阻断、未来启用条件。
- `final_output`: adapter 摘要和下一 Lab 指向。
- `risk_disclosure`: 财经输出边界提示。

每条 `AdapterResult` 固定包含：

- `adapter_name`
- `provider_mode`
- `capability`
- `input_summary`
- `output`
- `status`
- `error`
- `requires_api_key`
- `requires_human_confirmation`

## Demo

运行默认 demo：

```powershell
python labs/08-mx-skills-adapter/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 08-mx-skills-adapter
```

查看 real stub 的阻断效果：

```powershell
python labs/08-mx-skills-adapter/demo/run_demo.py --adapter-mode real-mx-stub
```

输出完整 JSON：

```powershell
python labs/08-mx-skills-adapter/demo/run_demo.py --json
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 08-mx-skills-adapter
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 不做什么

- 不使用 `.agents/` 或 `.codex` 作为仓库内容。
- 不调用真实模型 API、真实向量数据库或真实财经 API。
- 不读取真实 `MX_APIKEY`，不发送网络请求，不保存 authenticated response。
- 不生成真实股票推荐、收益承诺、交易动作或目标价格。
- 不让真实 provider 自动启用。

## 和前后 Lab 的关系

- Lab 07 负责 Skill Generation，生成可审查 Skill draft。
- Lab 08 负责 MX Skills Adapter，把 mock 工具和未来真实 Skills 放到统一 adapter contract 下。
- Lab 09 会进入 Research Planner DAG，把 adapter 能力纳入有状态研究计划。
