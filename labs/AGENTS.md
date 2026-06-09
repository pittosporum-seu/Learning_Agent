# Labs Rules

## Scope

These rules apply to everything under `labs/`.

## Required Reading

Before modifying any Lab, read:

- `AGENTS.md`
- `docs/product/lab-plan.md`
- `docs/product/security-and-secrets.md`
- `labs/README.md`
- The target Lab `README.md`
- The target Lab `AGENTS.md`, if present
- `labs/shared/` docs if the Lab uses shared case material

## Lab Contract

- Each Lab must teach one primary Agent concept.
- Each Lab must be mock-first and run without real API keys.
- Each runnable Lab must have a `README.md`, demo entry, tests, and stable structured output.
- Outputs must be observable, testable, and replayable through JSON, trace, logs, or deterministic fixtures.
- Do not generate real stock recommendations, certain returns, automatic trades, or unconfirmed trading actions.
- Any finance-facing output must carry risk disclosure and human confirmation boundaries.

## Implementation Rules

- Prefer deterministic local logic for teaching baselines.
- Real model or finance provider paths must be optional, environment-gated, and safe when keys are missing.
- Do not write real provider responses or secrets into `outputs/`, fixtures, docs, or logs.
- When a Lab changes, sync its README, `labs/README.md`, `docs/product/lab-plan.md`, `TODO.md`, `roadmap.md`, and `docs/document-graph.md` if behavior, status, or structure changes.
- When adding, completing, or changing Lab status, also sync `README.md`, `docs/start-here.md`, `docs/product/README.md`, `docs/product/showcase-framework.md`, and ensure `scripts/audit-related-docs.ps1` passes its dynamic Lab navigation audit.

## Checks

Run the target Lab tests and then all Lab tests:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab <lab-folder>
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
