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

## Structured Trace

Lab 02 的重点不是最终摘要，而是每一轮 loop 为什么这样走。每条 `trace` 事件都固定展示：

| 字段 | 含义 |
| --- | --- |
| `turn` | 当前 loop 轮次。 |
| `observation` | 本轮开始时系统观察到的状态。 |
| `decision` | 系统对下一步的判断。 |
| `why_this_action` | 为什么此刻要执行这个动作。 |
| `action` | 实际执行的动作。 |
| `result` | 结构化动作结果，包含 `ok`、`summary` 和关键字段。 |
| `guardrail_triggered` | 是否触发安全边界或 fail-closed 保护。 |
| `next_action_hint` | 下一轮应该去哪里，或为什么停止。 |
| `status` | 执行动作后的 loop 状态。 |

典型 agent 路径会产生：

```json
[
  {
    "turn": 1,
    "observation": "No StrategySpec yet.",
    "decision": "Parse the natural-language request before planning.",
    "why_this_action": "The loop cannot decide or plan until the natural-language request becomes a StrategySpec.",
    "action": "parse_strategy",
    "result": {
      "ok": true,
      "summary": "Parsed request into StrategySpec with execution_mode=agent and routing_mode=agent.",
      "execution_mode": "agent",
      "routing_mode": "agent",
      "matched_signals": ["time_sensitive", "multi_condition", "risk_filter", "watchlist_output"]
    },
    "guardrail_triggered": false,
    "next_action_hint": "Next loop should build a mock research plan.",
    "status": "running"
  },
  {
    "turn": 2,
    "observation": "StrategySpec is ready; research plan has not been built.",
    "decision": "Build a research plan from the valid StrategySpec.",
    "why_this_action": "The StrategySpec is complete enough to produce a mock research plan without calling real tools.",
    "action": "build_research_plan",
    "result": {
      "ok": true,
      "summary": "Built research plan with 5 steps.",
      "plan_step_count": 5,
      "planned_tools": ["mx-xuangu-mock", "mx-data-mock", "mx-search-mock"],
      "requires_human_confirmation": true
    },
    "guardrail_triggered": false,
    "next_action_hint": "Next loop should finalize the planning summary.",
    "status": "running"
  },
  {
    "turn": 3,
    "observation": "Research plan is ready; final output has not been prepared.",
    "decision": "Prepare final output and stop the loop.",
    "why_this_action": "The mock research plan is ready, so the loop can prepare the handoff summary for later Labs.",
    "action": "finalize",
    "result": {
      "ok": true,
      "summary": "Strategy Agent Loop completed a mock planning pass.",
      "next_lab": "Lab 03 will replace mock_tool placeholders with callable mock finance tools."
    },
    "guardrail_triggered": false,
    "next_action_hint": "Loop is complete; Lab 03 can consume the mock_tool placeholders later.",
    "status": "completed"
  }
]
```

缺信息、禁止动作和 `max_turns` 超限会把 `guardrail_triggered` 置为 `true`，并让状态进入 `blocked` 或 `failed`，不会继续生成投研计划。

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
