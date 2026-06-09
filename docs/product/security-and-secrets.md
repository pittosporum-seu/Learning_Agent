# 密钥、安全与合规边界

个性化投研 Agent 系统会接触模型 API、财经数据 API、模拟组合和用户偏好，因此安全边界必须从第一天进入设计。

## 密钥来源

真实密钥不写进仓库。运行时由 Hermes 或受信任的本地环境提供，再暴露为环境变量。

| 环境变量 | 用途 | 来源 |
| --- | --- | --- |
| `LLM_API_KEY` | 调用 OpenAI-compatible 模型 provider | Hermes 或本地环境 |
| `LLM_BASE_URL` | OpenAI-compatible 基础地址 | Hermes 或本地环境 |
| `LLM_MODEL` | 模型名 | Hermes 或本地环境 |
| `LLM_PROVIDER_LABEL` | Web demo 中展示的 provider 名称 | Hermes 或本地环境 |
| `LLM_CHAT_COMPLETIONS_URL` | 可选，OpenAI-compatible chat completions 端点 | Hermes 或本地环境 |
| `XIAOMI_API_KEY` | Xiaomi MiMo 兼容别名，可映射到 `LLM_API_KEY` | Hermes |
| `XIAOMI_BASE_URL` | Xiaomi MiMo 兼容别名，可映射到 `LLM_BASE_URL` | Hermes |
| `XIAOMI_MODEL` | Xiaomi MiMo 兼容别名，可映射到 `LLM_MODEL` | Hermes |
| `MIMO_API_KEY` | 旧版兼容别名，优先级低于 `LLM_*` 和 `XIAOMI_*` | Hermes |
| `MIMO_CHAT_COMPLETIONS_URL` | 旧版兼容别名 | Hermes 或本地环境 |
| `MIMO_BASE_URL` | 旧版兼容别名 | Hermes 或本地环境 |
| `MIMO_MODEL` | 旧版兼容别名 | Hermes 或本地环境 |
| `FINANCE_PROVIDER_PROFILE` | 可选外部财经 provider profile，当前示例为 `mx-skills` | 本地环境 |
| `FINANCE_PROVIDER_API_KEY` | 可选外部财经 provider key | Hermes 或本地环境 |
| `FINANCE_PROVIDER_BASE_URL` | 可选外部财经 provider 基础地址 | Hermes 或本地环境 |
| `FINANCE_PROVIDER_ALLOW_REAL` | 手动允许外部 provider 的环境闸门，必须为 `true` 才能启用 | 本地环境 |
| `FINANCE_PROVIDER_TIMEOUT_SECONDS` | 可选外部 provider 请求超时秒数 | 本地环境 |
| `FINANCE_PROVIDER_API_KEY_HEADER` | 可选外部 provider key header 名称 | 本地环境 |
| `MX_APIKEY` | `mx-skills` profile 的兼容 key 名 | Hermes 或本地环境 |
| `MX_API_URL` | 可选，`mx-skills` profile 的 API 基础地址 | Hermes 或本地环境 |
| `MX_SKILLS_BASE_URL` | 可选 `mx-skills` profile 基础地址 | Hermes 或本地环境 |
| `MX_BASE_URL` | `MX_SKILLS_BASE_URL` 的兼容别名 | Hermes 或本地环境 |
| `MX_ALLOW_REAL_PROVIDER` | `FINANCE_PROVIDER_ALLOW_REAL` 的兼容别名 | 本地环境 |
| `MX_TIMEOUT_SECONDS` | `FINANCE_PROVIDER_TIMEOUT_SECONDS` 的兼容别名 | 本地环境 |

Lab 01 的本地启动脚本可以把 Hermes 中的 Xiaomi MiMo 配置映射到 `LLM_*`。示例 base URL：

```text
https://token-plan-sgp.xiaomimimo.com/v1
```

解析优先级是 `LLM_*` 高于 `XIAOMI_*`，`XIAOMI_*` 高于 `MIMO_*`。Web demo 默认使用规则基线，不会因为检测到模型配置就自动调用模型。

仓库只保留 `.env.example`。本地可以使用 `.env` 或系统环境变量，但 `.env` 和 `.env.*` 不能进入仓库。

## 提交前检查

每次提交前至少运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
```

`scripts/check-secrets.ps1` 负责扫描非忽略文件，阻止明显的密钥、token、Bearer 凭据和真实环境变量值进入仓库。

## 不能提交的内容

- 真实 API key、token、cookie、session、password。
- 真实账户信息、手机号、身份证、银行卡、资金账户信息。
- 带认证头的请求日志。
- 可能包含敏感 header 的原始响应文件。
- `.env`、`.env.local`、`.env.production` 等真实环境文件。

允许提交：

- `.env.example` 中的占位符。
- mock 数据。
- 不含凭据的接口结构说明。
- 不含个人隐私的测试样例。

## 财经输出边界

系统可以推荐候选股票进入观察池，但必须满足：

- 说明数据来源和检索时间。
- 给出关键证据和不确定性。
- 保留风险提示。
- 明确不构成投资建议或收益承诺。
- 真实交易前必须由用户独立判断。

禁止输出：

- 保证收益、稳赚、必涨等确定性表述。
- 绕过用户确认的买卖指令。
- 没有证据来源的个股推荐。
- 把模拟组合表现说成真实可复制收益。

## 人工确认规则

以下动作必须人工确认：

- 添加或删除自选股。
- 进入模拟组合。
- 模拟买入、卖出、撤单。
- 将某个流程固化为正式 Skill。
- 切换到真实财经数据源。
- 对外发布包含候选股票的报告。

## 测试策略

测试默认使用 mock：

- mock 模型响应。
- mock 东方财富妙想 Skills 输出。
- mock 用户偏好。
- mock 新闻、公告、行情和财务数据。

真实 API 只在手动集成测试或本地 Web demo 中使用，并且不把真实响应中的敏感信息写入仓库。

## 外部财经 Provider 启用条件

Lab 08 默认只走 `mock-finance`。`external-finance` 外部 provider 路径必须同时满足：

- adapter mode 为 `external-finance`。
- 命令行显式传入 `--allow-real-provider`。
- `FINANCE_PROVIDER_ALLOW_REAL=true` 或 `MX_ALLOW_REAL_PROVIDER=true`。
- `FINANCE_PROVIDER_API_KEY` 或 `MX_APIKEY` 存在。
- 可选提供 `FINANCE_PROVIDER_BASE_URL`、`MX_SKILLS_BASE_URL`、`MX_BASE_URL` 或 `MX_API_URL`；`mx-skills` profile 未配置时使用默认公开 endpoint。

任一条件不满足时，必须 fail closed：

- 不发送网络请求。
- `status=blocked`。
- `network_request_sent=false`。
- `api_key_present` 只表示 key 是否存在，不输出 key 内容。
- `raw_response_persisted=false`。

真实 provider 响应不能写入 tracked 文件，不能写入 `outputs/` 中除 `.gitkeep` 外的文件，不能提交到 `provider_responses/` 或 `authenticated_responses/`。`adapter_trace` 只能保存状态、字段名、计数和错误摘要，不能保存 raw authenticated response。MX Skills 只是一个可选 provider profile，需要的人可自行安装或配置，不作为仓库本地 runtime 目录提交。
