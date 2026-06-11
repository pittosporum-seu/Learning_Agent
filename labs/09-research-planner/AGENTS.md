# Lab 09 Rules

## Scope

These rules apply to `labs/09-research-planner/`.

## Teaching Goal

Lab 09 demonstrates Research Planner DAG / Agent Harness. It turns Lab 08 Finance Provider Adapter output into a stateful DAG with dependencies, trace, failure propagation, and human confirmation boundaries.

## Required Contract

- The DAG must include `parse_and_route`, `adapter_capability_check`, `candidate_generation`, `market_data_check`, `news_risk_check`, `evidence_context_attach`, `memory_preference_adjustment`, `skill_selection`, and `human_review_gate`.
- Every node must expose `node_id`, `node_type`, `depends_on`, `status`, `inputs`, `outputs`, `requires_human_confirmation`, and `failure_behavior`.
- `planner_trace` must explain each node status transition with `node_id`, `status`, `reason`, `dependency_status`, `started_from`, `produced_outputs`, `blocked_reason`, and `skipped_reason`.
- Upstream `blocked` or `skipped` nodes must cause dependent nodes to become `skipped` or `blocked`; they must not continue as normal `completed`.
- `human_review_gate` must not auto-complete. The normal mock path ends at `waiting_human_confirmation`.
- Missing `risk_disclosure` must block `human_review_gate`.

## Boundaries

- Do not call real model APIs, real vector databases, or real finance APIs.
- Do not execute adapter calls in Lab 09; consume Lab 08 output only.
- Do not generate investment advice, guaranteed returns, trading actions, or target prices.
- Do not create `.agents/` or `.codex/`.
- Tests must run without real keys or real provider responses.
