# Lab 06 Rules

## Scope

This Lab demonstrates Skill Registry for the Learning_Agent investment research teaching case.

## Concept Boundary

- Primary concept: Skill Registry with local mock Skill metadata.
- Skills are repository learning artifacts, not Codex runtime skills.
- Do not use `.agents/` or `.codex/` as repository content.
- Skill selection may produce candidate abilities, but it must not execute trades or generate investment advice.

## Hard Boundaries

- Do not call real model APIs, vector databases, finance APIs, or news services.
- Do not store real user identity, private financial data, keys, sessions, or provider responses.
- Do not select execution-oriented Skills when upstream output is blocked.
- Skills that hand off watchlists or simulation plans must require human confirmation.
- Missing risk disclosure, missing evidence, or insufficient adjusted evidence must disable high-risk Skills.

## Required Output

- `registered_skills`
- `skill_selection_trace`
- `selected_skills`
- `disabled_skills`
- `risk_disclosure`
- `next_lab: Lab 07 Skill Generation`

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 06-skill-registry
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
