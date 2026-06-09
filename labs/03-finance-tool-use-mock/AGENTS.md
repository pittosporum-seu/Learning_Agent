# Lab 03 Rules

## Teaching Goal

Lab 03 demonstrates Tool Use with mock finance tools. It shows tool registration, tool selection, structured inputs, structured outputs, failure handling, `tool_trace`, and `candidate_evidence`.

## Boundaries

- Use only local mock data from this Lab.
- Do not call real finance APIs, model APIs, market data, news services, or 东方财富妙想 Skills.
- Do not output investment advice, certain returns, trading actions, or real stock recommendations.
- Candidate output is a mock observation pool for learning Tool Use only.
- Tool results must become structured evidence before they appear in final output.
- Keep `risk_disclosure` in every successful or blocked run.

## Required Checks

When changing Lab 03, cover:

- tool registry lookup
- `select_candidates`
- `fetch_market_data`
- `search_finance_news`
- `tool_trace`
- `candidate_evidence`
- blocked requests that do not call tools
- no `buy`, `sell`, `recommendation`, or `target_price` fields in outputs
