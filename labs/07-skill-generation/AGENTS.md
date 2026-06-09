# Lab 07 Rules

## Scope

This Lab demonstrates Skill Generation for the Learning_Agent investment research teaching case.

## Boundaries

- Primary concept: generate a reviewable Skill draft from stable mock workflow outputs.
- Use Lab 06 output as input; do not use real Codex skill runtime.
- Do not write generated drafts into `.agents/`, `.codex/`, or any local runtime config directory.
- Do not auto-enable generated Skills.
- Do not call real model APIs, vector databases, finance APIs, or real user stores.
- Do not generate investment advice, certain returns, trading actions, or target prices.
- Keep `risk_disclosure` and human review boundaries in every normal output.

## Required Output

- `skill_registry_output`
- `generated_skill_draft`
- `skill_draft_markdown`
- `draft_review`
- `final_output`
- `risk_disclosure`
- `next_lab: Lab 08 Finance Provider Adapter`

## Draft Requirements

The draft must include:

- `name`
- `description`
- `trigger_scenarios`
- `disabled_scenarios`
- `inputs`
- `outputs`
- `workflow_steps`
- `human_confirmation_points`
- `safety_boundaries`
- `test_cases`

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 07-skill-generation
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
