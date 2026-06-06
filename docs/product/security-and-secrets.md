# 密钥、安全与合规边界

个性化投研 Agent 系统会接触模型 API、财经数据 API、模拟组合和用户偏好，因此安全边界必须从第一天进入设计。

## 密钥来源

真实密钥不写进仓库。运行时由 Hermes 或受信任的本地环境提供，再暴露为环境变量。

| 环境变量 | 用途 | 来源 |
| --- | --- | --- |
| `MIMO_API_KEY` | 调用小米 MiMo 模型 | Hermes |
| `XIAOMI_API_KEY` | `MIMO_API_KEY` 的兼容别名 | Hermes |
| `XIAOMI_BASE_URL` | 小米 MiMo OpenAI-compatible 基础地址，Hermes canonical 变量 | Hermes |
| `XIAOMI_MODEL` | 小米 MiMo 模型名，Hermes canonical 变量 | Hermes |
| `MIMO_CHAT_COMPLETIONS_URL` | 可选，MiMo OpenAI-compatible chat completions 端点 | Hermes 或本地环境 |
| `MIMO_BASE_URL` | 可选，自定义兼容网关基础地址 | Hermes 或本地环境 |
| `MIMO_MODEL` | 可选，默认 `mimo-v2.5` | Hermes 或本地环境 |
| `MX_APIKEY` | 调用东方财富妙想 Skills | Hermes |
| `MX_API_URL` | 可选，妙想 API 基础地址 | Hermes 或本地环境 |

Lab 01 默认使用：

```text
https://token-plan-sgp.xiaomimimo.com/v1
```

解析优先级是 `XIAOMI_*` 高于 `MIMO_*`，与 Hermes 的 `provider: xiaomi` 配置保持一致。

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

- mock MiMo 响应。
- mock 东方财富妙想 Skills 输出。
- mock 用户偏好。
- mock 新闻、公告、行情和财务数据。

真实 API 只在手动集成测试或本地 Web demo 中使用，并且不把真实响应中的敏感信息写入仓库。
