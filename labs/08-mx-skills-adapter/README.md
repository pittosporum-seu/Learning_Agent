# Lab 08: MX Skills Adapter

这个 Lab 展示 `Adapter`：把 Lab 03 的 mock finance tools 和可选真实东方财富妙想 Skills provider 放到统一 adapter contract 下。它的定位是 mock-first，但保留手动跑通真实 provider 路径的能力。

默认 demo、默认 tests 和 CI 路径只使用 `mock-mx`，不读取真实 key，不发送真实网络请求。真实 provider 必须由用户本地显式配置环境变量，并在命令行传入 `--allow-real-provider` 后才可能启用。

本 Lab 不使用 `.agents/` 或 `.codex/` 作为仓库内容，不生成投资建议，不执行交易动作。

## Adapter 与 Tool / Skill / MCP 的区别

- Tool 是单个可调用能力，例如候选筛选、行情查询、资讯搜索。
- Skill 是稳定流程的能力声明，描述何时使用、如何使用和何时禁用。
- MCP 是把外部工具暴露给模型或 Agent 的协议生态。
- Adapter 是工程边界层，把不同 provider 的能力统一成同一个 contract，并把 mock-first、安全门和错误处理放在一处。

## 当前模式

| Adapter | Provider mode | 默认启用 | 说明 |
| --- | --- | --- | --- |
| `mock-mx` | `mock` | 是 | 复用 Lab 03 本地 mock 工具，默认可跑、无需 key。 |
| `real-mx-stub` | `real_stub` | 否 | 只返回 blocked，用于展示禁用形态，不读 key、不发请求。 |
| `real-mx` | `real` | 否 | 可选真实 provider 路径，必须手动配置环境变量并显式允许。 |

真实 provider 启用必须同时满足：

- `adapter_mode=real-mx`
- 命令行传入 `--allow-real-provider`
- `MX_ALLOW_REAL_PROVIDER=true`
- `MX_APIKEY` 存在
- `MX_SKILLS_BASE_URL` 或 `MX_BASE_URL` 存在

任一条件不满足时，系统返回 `blocked`，`network_request_sent=false`，不会发送请求。`api_key_present` 只表示 key 是否存在，不输出 key 内容。

## 输入

输入包含：

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- `adapter_mode`，默认 `mock-mx`。
- 可选 `capabilities`，默认 `mx-xuangu,mx-data,mx-search`。
- Lab 07 输出中的 Skill draft 和上游证据。

Lab 08 会先调用 Lab 07 的 `run_skill_generation`。如果上游 blocked，本 Lab 也 blocked，不调用 adapter。

## 输出

核心输出是结构化 JSON：

- `skill_generation_output`: Lab 07 的完整输出。
- `registered_adapters`: 当前注册的 `mock-mx`、`real-mx-stub` 和 `real-mx`。
- `adapter_mode`: 当前 adapter。
- `provider_mode`: 当前 provider mode。
- `adapter_trace`: 每次 adapter 调用的 `AdapterResult`。
- `safety_gate`: 真实 provider 是否允许、缺少哪些条件、是否存在 key、是否持久化 raw response。
- `real_provider_attempted`: 是否尝试真实 provider 路径。
- `real_provider_allowed`: 真实 provider 是否通过闸门。
- `final_output`: adapter 摘要和下一个 Lab 指向。
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
- `network_request_sent`
- `api_key_present`
- `raw_response_persisted`

`adapter_trace` 只保存摘要、字段名、计数、状态和错误原因，不保存 raw authenticated response。

## Demo

运行默认 mock demo：

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

查看完整 JSON：

```powershell
python labs/08-mx-skills-adapter/demo/run_demo.py --json
```

## 手动真实 Provider 路径

真实 provider 只用于本地手动验证。不要把 key 写入仓库，不要把 `.env.local`、真实响应、认证响应或 provider response 提交。

在 WSL / Hermes 或可信本地环境里注入环境变量：

```bash
export MX_APIKEY="injected-by-local-runtime"
export MX_SKILLS_BASE_URL="injected-by-local-runtime"
export MX_ALLOW_REAL_PROVIDER=true
```

然后显式运行：

```bash
python labs/08-mx-skills-adapter/demo/run_demo.py \
  --adapter-mode real-mx \
  --allow-real-provider \
  --json
```

如果使用本地 `.env.local` 辅助注入，必须确保它被 `.gitignore` 忽略。

## Manual Integration Test

默认测试不会跑真实 provider。手动 integration test 需要显式设置：

```bash
export RUN_REAL_MX_INTEGRATION=1
export MX_ALLOW_REAL_PROVIDER=true
export MX_APIKEY="injected-by-local-runtime"
export MX_SKILLS_BASE_URL="injected-by-local-runtime"

python labs/08-mx-skills-adapter/tests/manual_test_real_mx_adapter.py
```

手动测试不能打印 key，不能保存 raw response，只断言结果结构、安全字段和 `risk_disclosure` 存在。

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 08-mx-skills-adapter
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

默认 tests 覆盖：

- mock adapter 能跑 `mx-xuangu`、`mx-data`、`mx-search`。
- real adapter 缺 key 时 blocked，且不发请求。
- real adapter 缺 `--allow-real-provider` 时 blocked，且不发请求。
- real adapter 可以用 fake transport 单测成功路径。
- `adapter_trace` 不包含 key，不包含 raw authenticated response。
- 输出不包含 `buy`、`sell`、`recommendation`、`target_price`。
- 不创建 `.agents/` 或 `.codex/`。

## 不做什么

- 不默认调用真实模型 API、真实向量数据库或真实财经 API。
- 不提交真实 key、真实响应、本地 `.env.local` 或 Hermes 配置文件。
- 不把 raw provider response 写进 tracked 文件或 `adapter_trace`。
- 不生成真实股票推荐、收益承诺、交易动作或目标价格。
- 不让真实 provider 自动启用。

## 和前后 Lab 的关系

- Lab 07 负责 Skill Generation，生成可审查 Skill draft。
- Lab 08 负责 MX Skills Adapter，把 mock 工具和可选真实 Skills provider 放到统一 adapter contract 下。
- Lab 09 将进入 Research Planner DAG，把 adapter 能力纳入有状态研究计划。
