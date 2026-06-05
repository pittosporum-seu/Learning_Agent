# Lab 01: Strategy Intake

这个 Lab 解决第一件事：把用户自然语言里的投研想法解析成结构化 `StrategySpec`。

它对应 `Agent基础知识 01: Workflow vs Agent`。现在它同时提供两种入口：

- 规则基线：不调用外部 API，字段稳定，适合回归测试和安全边界验证。
- MiMo 解析：读取本地环境变量里的小米 MiMo key，真实调用模型，在规则基线上做语义补全、归一化和追问判断。

本 Lab 仍然不查真实行情，不调用东方财富妙想财经数据，不输出真实个股推荐，也不执行交易。它只负责把策略意图、筛选条件、风险边界和待确认问题整理清楚。

## 输入

自然语言策略，例如：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

## 输出

结构化 JSON，核心字段包括：

- `market`: 目标市场。
- `themes`: 主题或行业。
- `horizon_days`: 观察时间窗口。
- `candidate_rules`: 候选筛选规则。
- `risk_filters`: 风险过滤规则。
- `user_preferences`: 用户偏好。
- `execution_mode`: `workflow`、`agent` 或 `needs_clarification`。
- `clarification_questions`: 需要用户补充的问题。
- `prohibited_actions`: 不安全或不合规意图标签。
- `risk_disclosure`: 固定风险提示。

## 运行

规则基线命令行：

```powershell
python labs/01-strategy-intake/src/strategy_intake.py "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
```

运行默认样例：

```powershell
python labs/01-strategy-intake/src/strategy_intake.py
```

## MiMo 配置

MiMo 模式从本地环境变量读取 key，仓库只保留 `.env.example` 占位，不提交真实密钥。

```powershell
$env:XIAOMI_API_KEY="<read-from-hermes>"
$env:XIAOMI_BASE_URL="https://token-plan-sgp.xiaomimimo.com/v1"
$env:XIAOMI_MODEL="mimo-v2.5-pro"
```

Hermes 对应配置：

```text
provider: xiaomi
base_url: https://token-plan-sgp.xiaomimimo.com/v1
model: mimo-v2.5-pro
key_env: XIAOMI_API_KEY
```

如需走自定义网关，可以设置：

```powershell
$env:XIAOMI_CHAT_COMPLETIONS_URL="https://your-gateway.example/v1/chat/completions"
```

兼容变量 `MIMO_API_KEY`、`MIMO_BASE_URL`、`MIMO_MODEL` 仍可使用，但优先级低于 `XIAOMI_*`。

测试默认 mock MiMo 响应，不依赖真实 key。

## Web Demo

启动本地网页 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-web.ps1 -Lab 01-strategy-intake -Port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

网页会先做健康检查：如果检测到 `MIMO_API_KEY` 或 `XIAOMI_API_KEY`，默认切到 MiMo 解析；否则使用规则基线。MiMo 模式需要点击“解析”触发，避免输入时反复消耗 token。

在本机 Windows 环境下，`scripts/run-lab-web.ps1` 会尝试从 WSL Hermes 的 `.env` 中加载 `XIAOMI_API_KEY`、`XIAOMI_BASE_URL` 和 `XIAOMI_MODEL` 到当前 server 进程环境；不会打印或提交真实 key。

## Demo 脚本

运行内置 demo 样例：

```powershell
python labs/01-strategy-intake/demo/run_demo.py
```

也可以通过仓库脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake
```

传入自己的策略：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake -Request "找近 30 日趋势较强、成交活跃的新能源股票，生成观察池。"
```

输出完整 JSON：

```powershell
python labs/01-strategy-intake/demo/run_demo.py --json
```

把 demo 结果写到文件：

```powershell
python labs/01-strategy-intake/demo/run_demo.py --output labs/01-strategy-intake/outputs/demo_strategy_specs.json
```

## 测试

```powershell
python -m unittest discover -s labs/01-strategy-intake/tests
```

统一测试入口：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 01-strategy-intake
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 设计边界

- 规则基线和 MiMo 解析都只产出 `StrategySpec`。
- 不在这一层生成真实股票名单。
- 缺少主题、时间窗口或筛选规则时，输出待确认问题。
- 发现“稳赚”“必涨”“自动买入”等高风险请求时，转为风险边界提示。
- 所有输出固定包含风险提示。
- 真实 key 只从环境变量读取，提交前必须运行 `scripts/check-secrets.ps1`。

## 和后续 Lab 的关系

Lab 02 会把 `StrategySpec` 放进 Agent Loop，开始按步骤推进投研流程。

Lab 03 会把 `candidate_rules`、`risk_filters` 映射到 mock 财经工具调用。

Lab 08 以后再把 mock 工具适配到东方财富妙想 Skills，并在有人工确认和风险提示的前提下生成候选观察池。
