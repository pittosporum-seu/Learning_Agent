# Lab 02 Rules

## Teaching Goal

Lab 02 demonstrates Agent Loop + structured trace. It receives Lab 01 `StrategySpec`, then shows observe -> decide -> act -> result -> next action.

## Trace Contract

When modifying Lab 02 trace, ensure each trace event exposes:

- `observation`
- `decision`
- `why_this_action`
- `action`
- `result`
- `guardrail_triggered`
- `next_action_hint`
- `status`

The trace should make it clear what changed after each action and why the next action follows.

## Boundaries

- Do not connect Lab 02 to real model providers, market data, news, or 东方财富妙想 Skills.
- `research_plan` is only a plan for later Labs, not executed evidence collection.
- Missing information, high-risk requests, prohibited actions, and `max_turns` exhaustion must fail closed.
- Do not produce real stock lists, recommendations, or trading actions.

## Required Checks

When changing Lab 02, cover:

- agent request plan path
- workflow request plan path
- clarification / prohibited request blocked path
- max-turn failed path
- structured trace fields
