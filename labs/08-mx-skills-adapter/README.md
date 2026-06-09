# Lab 08: Finance Provider Adapter

这个 Lab 展示 `Adapter`：把 Lab 03 的 mock finance tools 和未来可选的外部财经 Skills / provider 放到统一 adapter contract 下。它的默认路径是 mock-first；真实 provider 只作为本地手动验证路径，不是仓库运行依赖。

MX Skills 是本 Lab 的一个 provider profile，名称为 `mx-skills`。需要真实 MX 能力的人可以自行安装或配置对应 provider，参考下载入口：[东方财富妙想](https://dl.dfcfs.com/m/itc4)。仓库不保存 `.agents/`、`.codex/`、真实 key、真实响应或本地运行配置。

## Adapter 和 Tool / Skill / MCP 的区别

- Tool 是单个可调用能力，例如候选筛选、行情查询、资讯检索。
- Skill 是稳定流程的能力声明，描述何时使用、如何使用和何时禁用。
- MCP 是把外部工具暴露给模型或 Agent 的协议生态。
- Adapter 是工程边界层，把不同 provider 的能力统一成同一个 contract，并把 mock-first、安全门和错误处理放在一处。

## 当前模式

| Adapter | Provider mode | 默认启用 | 说明 |
| --- | --- | --- | --- |
| `mock-finance` | `mock` | 是 | 复用 Lab 03 本地 mock 工具，默认可跑、无需 key。 |
| `external-finance-stub` | `external_stub` | 否 | 只返回 blocked，用于展示禁用形态，不读 key、不发请求。 |
| `external-finance` | `external` | 否 | 可选真实 provider 路径，必须手动配置环境变量并显式允许。 |

统一 capability 名称：

| Capability | MX profile 映射 | 说明 |
| --- | --- | --- |
| `candidate-screen` | `mx-xuangu` | 候选筛选信息。 |
| `market-data` | `mx-data` | 行情和财务类结构化信息。 |
| `finance-news` | `mx-search` | 新闻、公告、研报或政策检索信息。 |

旧名称 `mock-mx`、`real-mx-stub`、`real-mx`、`mx-xuangu`、`mx-data`、`mx-search` 仍作为兼容 alias 接受，但文档和输出默认使用通用名称。

真实 provider 启用必须同时满足：

- `adapter_mode=external-finance`
- 命令行传入 `--allow-real-provider`
- `FINANCE_PROVIDER_ALLOW_REAL=true` 或 `MX_ALLOW_REAL_PROVIDER=true`
- `FINANCE_PROVIDER_API_KEY` 或 `MX_APIKEY` 存在
- 可选配置 `FINANCE_PROVIDER_BASE_URL`、`MX_SKILLS_BASE_URL`、`MX_BASE_URL` 或 `MX_API_URL`；`mx-skills` profile 未配置时使用公开默认 endpoint

任一条件不满足时，系统返回 `blocked`，`network_request_sent=false`，不发送请求。`api_key_present` 只表示 key 是否存在，不输出 key 内容。

## 输入

输入包含：

- 自然语言投研策略。
- mock `user_id`，默认 `conservative_user`。
- `adapter_mode`，默认 `mock-finance`。
- 可选 `capabilities`，默认 `candidate-screen,market-data,finance-news`。
- Lab 07 输出中的 Skill draft 和上游证据。

Lab 08 会先调用 Lab 07 的 `run_skill_generation`。如果上游 blocked，本 Lab 也 blocked，不调用 adapter。

## 输出

核心输出是结构化 JSON：

- `skill_generation_output`: Lab 07 的完整输出。
- `registered_adapters`: 当前注册的 `mock-finance`、`external-finance-stub` 和 `external-finance`。
- `adapter_mode`: 当前 adapter。
- `provider_mode`: 当前 provider mode。
- `adapter_trace`: 每次 adapter 调用的 `AdapterResult`。
- `safety_gate`: 外部 provider 是否允许、缺少哪些条件、是否存在 key、是否持久化 raw response。
- `real_provider_attempted`: 是否尝试外部 provider 路径。
- `real_provider_allowed`: 外部 provider 是否通过安全门。
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

查看 external stub 的阻断效果：

```powershell
python labs/08-mx-skills-adapter/demo/run_demo.py --adapter-mode external-finance-stub
```

查看完整 JSON：

```powershell
python labs/08-mx-skills-adapter/demo/run_demo.py --json
```

## 手动真实 Provider 路径

真实 provider 只用于本地手动验证。不要把 key 写入仓库，不要把 `.env.local`、真实响应、认证响应或 provider response 提交。

通用 provider 环境变量：

```bash
export FINANCE_PROVIDER_PROFILE="mx-skills"
export FINANCE_PROVIDER_API_KEY="injected-by-local-runtime"
export FINANCE_PROVIDER_ALLOW_REAL=true
```

兼容 MX profile 的环境变量：

```bash
export MX_APIKEY="injected-by-local-runtime"
export MX_ALLOW_REAL_PROVIDER=true
```

然后显式运行：

```bash
python labs/08-mx-skills-adapter/demo/run_demo.py \
  --adapter-mode external-finance \
  --allow-real-provider \
  --capabilities candidate-screen \
  --json
```

如使用本地 `.env.local` 辅助注入，必须确保它被 `.gitignore` 忽略。

## Manual Integration Test

默认测试不会跑真实 provider。手动 integration test 需要显式设置：

```bash
export RUN_REAL_FINANCE_INTEGRATION=1
export FINANCE_PROVIDER_PROFILE="mx-skills"
export FINANCE_PROVIDER_ALLOW_REAL=true
export FINANCE_PROVIDER_API_KEY="injected-by-local-runtime"

python labs/08-mx-skills-adapter/tests/manual_test_real_mx_adapter.py
```

如果只使用 MX 兼容变量，也可以设置 `RUN_REAL_MX_INTEGRATION=1`、`MX_ALLOW_REAL_PROVIDER=true` 和 `MX_APIKEY`。

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

- mock adapter 能跑 `candidate-screen`、`market-data`、`finance-news`。
- external adapter 缺 key 时 blocked，且不发请求。
- external adapter 缺 `--allow-real-provider` 时 blocked，且不发请求。
- external adapter 可以用 fake transport 单测成功路径。
- legacy MX 名称会被规范化到通用名称。
- `adapter_trace` 不包含 key，不包含 raw authenticated response。
- 输出不包含 `buy`、`sell`、`recommendation`、`target_price`。
- 不创建 `.agents/` 或 `.codex/`。

## 不做什么

- 不默认调用真实模型 API、真实向量数据库或真实财经 API。
- 不提交真实 key、真实响应、本地 `.env.local` 或 Hermes 配置文件。
- 不把 raw provider response 写进 tracked 文件或 `adapter_trace`。
- 不生成真实股票推荐、收益承诺、交易动作或目标价格。
- 不让外部 provider 自动启用。

## 和前后 Lab 的关系

- Lab 07 负责 Skill Generation，生成可审查 Skill draft。
- Lab 08 负责 Finance Provider Adapter，把 mock 工具和可选外部 provider 放到统一 adapter contract 下。
- Lab 09 将进入 Research Planner DAG，把 adapter 能力纳入有状态研究计划。
