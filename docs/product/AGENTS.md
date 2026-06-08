# Product Docs Rules

## Scope

These rules apply to `docs/product/` and product-facing descriptions elsewhere in the repository.

## Required Reading

Before changing product docs, read:

- `AGENTS.md`
- `docs/product/README.md`
- `docs/product/personalized-investment-research-agent.md`
- `docs/product/showcase-framework.md`
- `docs/product/lab-plan.md`
- `docs/product/security-and-secrets.md`
- `labs/README.md`
- `TODO.md`
- `roadmap.md`

## Product Positioning

- The product case is a showcase framework for learning Agent systems through a realistic investment research scenario.
- Do not describe the case as a stock recommendation system or trading automation system.
- Keep the teaching goal visible: Workflow vs Agent, Agent Loop, Tool Use, RAG, Memory, Skills, Evaluation, Trace, and Safety.

## Sync Rules

- If the system vision changes, sync `personalized-investment-research-agent.md`, `README.md`, and `lab-plan.md`.
- If Lab sequence, status, or acceptance criteria change, sync `lab-plan.md`, `docs/product/README.md`, `labs/README.md`, `TODO.md`, `roadmap.md`, and `docs/document-graph.md`.
- If keys, providers, finance APIs, simulation, or human confirmation boundaries change, sync `security-and-secrets.md`, `.env.example`, `scripts/check-secrets.ps1`, and `hooks/content-update.md` as needed.
- Keep `showcase-framework.md` aligned with the product README, lab plan, and security document.

## Finance Boundaries

- Finance outputs are for learning demos and watchlist-style observation only.
- Require risk disclosure, evidence/source references, uncertainty, and human confirmation for candidate stocks, reports, watchlists, simulations, or Skill activation.
- Do not promise returns, certain price movement, or automatic trade execution.
- Keep real keys out of docs except placeholder names such as `LLM_API_KEY` and `MX_APIKEY`.
