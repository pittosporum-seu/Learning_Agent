---
name: docs-sync
description: Template for synchronizing Learning_Agent documentation structure, navigation, roadmap, TODO, and audit checks.
---

# Learning_Agent Docs Sync Template

This file is a documentation template, not local runtime configuration.

## Read First

Read:

1. `AGENTS.md`
2. `hooks/content-update.md`
3. `docs/start-here.md`
4. `docs/README.md`
5. `docs/document-graph.md`
6. `TODO.md`
7. `roadmap.md`

For product docs, also read `docs/product/AGENTS.md`. For Labs, also read `labs/AGENTS.md` and target Lab rules.

## Sync Targets

When docs structure or long-lived content changes, update relevant files among:

- `README.md`
- `docs/README.md`
- `docs/start-here.md`
- `docs/document-graph.md`
- `docs/product/README.md`
- `docs/product/showcase-framework.md`
- `docs/product/lab-plan.md`
- `docs/product/security-and-secrets.md`
- `labs/README.md`
- `resources/README.md`
- `roadmap.md`
- `TODO.md`
- affected directory READMEs
- `scripts/audit-related-docs.ps1`, when a durable invariant should be checked

## Content Rules

- Keep formal docs free of writing prompts, self-check notes, chat traces, and scratch text.
- Remove tracking query parameters from reference links.
- Keep finance content framed as learning demos, evidence, watchlists, risk disclosure, and human confirmation.
- Do not present the investment research case as an advisory or trading system.
- Do not modify `docs/foundations/*.md`正文 unless explicitly requested.

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
