# Lab 05 Rules

## Scope

This Lab demonstrates User Preference Memory for the Learning_Agent investment research teaching case.

## Concept Boundary

- Primary concept: Memory with local mock user preferences.
- Memory may influence `max_candidates`, `excluded_themes`, `excluded_risk_flags`, and `report_style`.
- Memory creates an adjusted evidence view; it must not mutate original evidence.

## Hard Boundaries

- Do not store real user identity, account data, private financial data, or sensitive personal information.
- Do not call real model APIs, vector databases, finance APIs, or news services.
- Do not let Memory override `risk_disclosure`, remove sources, skip guardrails, or create investment advice.
- High-risk or incomplete requests must remain blocked even when Memory exists.
- Keep outputs deterministic, observable, and testable without real keys.

## Required Output

- `memory_snapshot`
- `memory_trace`
- `rag_output`
- `preference_application`
- `preference_adjusted_evidence`
- `risk_disclosure`
- `next_lab: Lab 06 Skill Registry`

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 05-user-preference-memory
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
