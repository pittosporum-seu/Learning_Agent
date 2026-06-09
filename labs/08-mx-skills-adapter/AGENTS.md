# Lab 08 Rules

## Scope

This Lab demonstrates a mock-first Finance Provider Adapter with an optional manually gated external provider path for the Learning_Agent investment research teaching case.

## Boundaries

- Primary concept: adapter contract for mock finance tools and optional external finance providers.
- Default provider must be `mock-finance`.
- Canonical capabilities are `candidate-screen`, `market-data`, and `finance-news`.
- MX names are compatibility aliases only: `mock-mx`, `real-mx-stub`, `real-mx`, `mx-xuangu`, `mx-data`, and `mx-search`.
- `external-finance-stub` must remain blocked and must not read keys or send network requests.
- `external-finance` may send a request only when adapter mode is `external-finance`, CLI passes `--allow-real-provider`, an allow env flag is true, and an API key exists in environment variables.
- Do not load `.agents/` or `.codex/` as provider runtime dependencies.
- Do not print secrets or persist raw authenticated responses.
- Do not generate investment advice, certain returns, trading actions, or target prices.
- Keep `risk_disclosure`, `safety_gate`, and human confirmation boundaries in all normal outputs.

## Provider Profiles

- `mx-skills` is a supported profile, not a repository dependency.
- Users who need MX provider capabilities can install or configure them separately from the repository.
- Other providers may be added if they can satisfy the same canonical capability contract.

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
