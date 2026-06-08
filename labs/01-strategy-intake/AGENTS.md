# Lab 01 Rules

## Teaching Goal

Lab 01 demonstrates Strategy Intake + Workflow/Agent Router. It turns a natural-language investment research request into `StrategySpec` and explains routing through `routing_decision`.

## Required Core Fields

Preserve these fields in outputs and tests:

- `StrategySpec`
- `execution_mode`
- `requires_agent`
- `routing_decision`
- `routing_decision.mode`
- `routing_decision.reason`
- `routing_decision.matched_signals`
- `routing_decision.next_step`
- `routing_decision.not_selected`
- `clarification_questions`
- `prohibited_actions`
- `risk_disclosure`

## Required Samples

Keep coverage for these four teaching cases:

- Workflow: `筛选市盈率小于20的银行股`
- Agent: `找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。`
- Needs clarification: `帮我找一些适合观察的股票`
- Blocked: `直接告诉我明天必涨的股票并自动买入`

## Boundaries

- Do not query real market data, news, announcements, or finance APIs in this Lab.
- Do not generate stock lists, recommendations, or trading actions.
- The default web and test path must remain rules-first and no-key runnable.
- Model parsing may only provide optional semantic completion; it must not weaken safety routing or require real keys in tests.
