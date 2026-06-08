# Repository Rules for Codex

## Purpose

This repository is an Agent learning showcase system. It should help readers learn Agent concepts through clear documents, runnable Labs, traceable demos, tests, and reusable Skills.

The investment research scenario is a teaching case. It is not an investment advisory product, does not promise returns, and must not bypass human confirmation for trading, watchlists, simulation portfolios, or Skill activation.

## Required Reading

Before changing Product docs, Labs, Skills, engineering docs, scripts, or navigation, read:

- `docs/start-here.md`
- `docs/product/README.md`
- `docs/product/lab-plan.md`
- `docs/product/security-and-secrets.md`
- `labs/README.md`
- `TODO.md`
- `roadmap.md`
- `hooks/content-update.md`

Also read the nearest `AGENTS.md` in the target directory and the target README.

## Hard Boundaries

- Do not commit real API keys, tokens, cookies, sessions, account data, or `.env` files.
- Real keys may only be read from environment variables or trusted local runtime; never print or persist them.
- Tests must pass without real keys by using mock data, mock model responses, or deterministic local fixtures.
- Do not present candidate stocks, watchlists, reports, or simulation results as investment advice.
- Do not output guaranteed returns, certain price movement, or automatic trading instructions.
- Keep risk disclosure and human confirmation boundaries in any finance-facing output.
- Do not edit `docs/foundations/*.md`正文 unless the user explicitly asks for foundation article edits.
- Do not add tracking query parameters to reference links.

## Change Discipline

- Keep each Lab focused on one Agent concept.
- Prefer mock-first implementations; real providers must be optional and environment-gated.
- When changing Product, Labs, Skills, or docs structure, sync relevant navigation and status files: `README.md`, `docs/README.md`, `docs/document-graph.md`, `roadmap.md`, `TODO.md`, and affected READMEs.
- Use `hooks/content-update.md` as the maintenance checklist for docs and Lab changes.
- Preserve formal docs only; do not commit writing prompts, self-check notes, chat traces, or scratch content.

## Required Checks

Before reporting completion, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

For a Lab-specific change, also run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab <lab-folder>
```

## Completion Report

Use this structure:

1. One-sentence conclusion.
2. Added files.
3. Modified files.
4. Checks run and results.
5. Risks or unfinished items.
