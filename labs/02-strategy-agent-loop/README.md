# Lab 02: Strategy Agent Loop

这个 Lab 接住 Lab 01 的 `StrategySpec`，演示一个最小 Agent Loop：观察当前状态、决定下一步、执行一步、记录 trace，最后产出投研流程计划或待确认状态。

它对应 `Agent基础知识 02: Agent Loop`。当前仍然不查真实行情、不查新闻、不生成股票名单；它只演示 Agent 的执行骨架。

## 输入

自然语言投研策略，例如：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

Lab 02 会先复用 Lab 01 的规则基线解析器，把输入转换为 `StrategySpec`，再进入 loop。

## 输出

结构化 JSON，核心字段包括：

- `request`: 原始请求。
- `status`: `completed`、`blocked` 或 `failed`。
- `strategy_spec`: Lab 01 解析出的结构化策略。
- `research_plan`: 根据策略生成的投研流程计划。
- `trace`: 每一轮 loop 的观察、决策、动作和结果。
- `final_output`: 面向后续 Lab 的摘要。

## Demo

运行内置 demo：

```powershell
python labs/02-strategy-agent-loop/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 02-strategy-agent-loop
```

传入自己的策略：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 02-strategy-agent-loop -Request "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
```

输出完整 JSON：

```powershell
python labs/02-strategy-agent-loop/demo/run_demo.py --json
```

## 测试

```powershell
python -m unittest discover -s labs/02-strategy-agent-loop/tests
```

或运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## Loop 设计

当前 loop 是确定性的教学基线：

```text
observe state
decide next action
execute action
record trace
repeat until completed, blocked, or failed
```

典型路径：

```text
parse_strategy
-> build_research_plan
-> finalize
```

需要追问或高风险请求：

```text
parse_strategy
-> request_clarification
-> blocked
```

超过最大轮次：

```text
max_turns guardrail
-> failed
```

## 设计边界

- 不查行情、不查新闻、不生成股票名单。
- 不直接接真实模型 provider，也不直接接东方财富妙想 Skills。
- `research_plan` 只是后续工具调用计划，不代表已经执行。
- 每一步必须写入 trace，方便调试、审计和回归。
- 真实工具调用会放在 Lab 03 以后。

## 和后续 Lab 的关系

Lab 03 会把 `research_plan` 里的 `mock_tool` 占位替换成可调用的 mock 财经工具。

Lab 09 会把当前线性 plan 升级成有状态 DAG。
