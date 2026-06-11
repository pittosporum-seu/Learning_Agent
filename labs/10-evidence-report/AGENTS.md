# Lab 10 Rules

## Scope

These rules apply to `labs/10-evidence-report/`.

## Teaching Goal

Lab 10 demonstrates Evidence Report generation. It turns Lab 09 Research Planner DAG output into a sourced, reviewable mock report draft with evidence references, limitations, risk disclosure, and human review boundaries.

## Required Contract

- The report must be built from `planner_output`, `adapter_trace`, `candidate_evidence`, `retrieved_context`, and `planner_trace`.
- The output must include `evidence_report`, `report_generation_trace`, `evidence_refs`, `risk_disclosure`, and `human_review_required=true`.
- Report status must be `needs_human_review` or `blocked`; helper models may also accept `draft`.
- Every candidate observation must include `evidence_refs`.
- Every evidence table item must include `source_type`, `source_name`, `claim`, `value_summary`, `limitations`, and `confidence`.
- Blocked Lab 09 output must produce a blocked report with evidence gaps instead of normal report conclusions.

## Boundaries

- Do not call real model APIs, real vector databases, or real finance APIs.
- Do not generate investment advice, guaranteed returns, trading actions, or target prices.
- Do not create `.agents/` or `.codex/`.
- Do not persist raw provider responses or secrets.
- Tests must run without real keys or real provider responses.
