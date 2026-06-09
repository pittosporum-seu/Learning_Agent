---
name: lab-implementation
description: Template for implementing or modifying Learning_Agent Labs while preserving mock-first behavior, tests, and documentation sync.
---

# Learning_Agent Lab Implementation Template

This file is a documentation template, not local runtime configuration.

## Read First

Read, in order:

1. `AGENTS.md`
2. `labs/AGENTS.md`
3. Target Lab `AGENTS.md`, if present
4. `docs/product/lab-plan.md`
5. `docs/product/security-and-secrets.md`
6. Target Lab `README.md`
7. `TODO.md`
8. `roadmap.md`

## Workflow

1. Identify the single Agent concept the Lab must teach.
2. Keep the implementation mock-first and runnable without real keys.
3. Update code, demo, tests, and README together when behavior changes.
4. Keep outputs structured, observable, testable, and replayable.
5. Preserve risk disclosure and human confirmation boundaries for finance-facing outputs.
6. Sync `labs/README.md`, `docs/product/lab-plan.md`, `docs/document-graph.md`, `TODO.md`, and `roadmap.md` when Lab status, structure, or behavior changes.

## Prohibitions

- Do not output real investment advice, guaranteed returns, certain price movement, or automatic trading actions.
- Do not commit or print real keys, tokens, cookies, account data, or raw authenticated responses.
- Do not make tests depend on real model or finance APIs.
- Do not remove demo or test coverage for existing teaching paths.

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab <lab-folder>
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
```
