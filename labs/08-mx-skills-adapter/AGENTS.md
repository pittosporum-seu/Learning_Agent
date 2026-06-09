# Lab 08 Rules

## Scope

This Lab demonstrates a mock-first MX Skills Adapter for the Learning_Agent investment research teaching case.

## Boundaries

- Primary concept: Adapter contract for mock finance tools and future external Skills.
- Default provider must be mock.
- Real provider must remain a stub in this Lab.
- Do not read real keys, print secrets, or send network requests.
- Do not use `.agents/` or `.codex/` as repository content.
- Do not generate investment advice, certain returns, trading actions, or target prices.
- Keep `risk_disclosure`, `safety_gate`, and human confirmation boundaries in all normal outputs.

## Required Output

- `skill_generation_output`
- `registered_adapters`
- `adapter_mode`
- `adapter_trace`
- `safety_gate`
- `final_output`
- `risk_disclosure`
- `next_lab: Lab 09 Research Planner DAG`

## Adapter Contract

Each `AdapterResult` must expose:

- `adapter_name`
- `provider_mode`
- `capability`
- `input_summary`
- `output`
- `status`
- `error`
- `requires_api_key`
- `requires_human_confirmation`

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 08-mx-skills-adapter
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
