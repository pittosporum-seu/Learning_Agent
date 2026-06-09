# Lab 08 Rules

## Scope

This Lab demonstrates a mock-first MX Skills Adapter with an optional manually gated real provider path for the Learning_Agent investment research teaching case.

## Boundaries

- Primary concept: Adapter contract for mock finance tools and optional external Skills.
- Default provider must be mock.
- `real-mx-stub` must remain blocked and must not read keys or send network requests.
- `real-mx` may send a request only when adapter mode is `real-mx`, CLI passes `--allow-real-provider`, `MX_ALLOW_REAL_PROVIDER=true`, `MX_APIKEY` exists, and `MX_SKILLS_BASE_URL` or `MX_BASE_URL` exists.
- Do not print secrets or persist raw authenticated responses.
- Do not use `.agents/` or `.codex/` as repository content.
- Do not generate investment advice, certain returns, trading actions, or target prices.
- Keep `risk_disclosure`, `safety_gate`, and human confirmation boundaries in all normal outputs.

## Required Output

- `skill_generation_output`
- `registered_adapters`
- `adapter_mode`
- `provider_mode`
- `adapter_trace`
- `safety_gate`
- `real_provider_attempted`
- `real_provider_allowed`
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
- `network_request_sent`
- `api_key_present`
- `raw_response_persisted`

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 08-mx-skills-adapter
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
