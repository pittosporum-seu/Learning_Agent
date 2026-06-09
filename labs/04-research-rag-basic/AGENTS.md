# Lab 04 Rules

## Scope

This Lab demonstrates Research RAG Basic for the Learning_Agent investment research teaching case.

## Concept Boundary

- Primary concept: RAG with local mock documents.
- Use local markdown files as the knowledge base.
- Use simple keyword retrieval so readers can inspect why each chunk was selected.
- Connect `retrieved_context` to Lab 03 `candidate_evidence`.

## Hard Boundaries

- Do not call real model APIs, vector databases, finance APIs, or news services.
- Do not generate investment advice, buy/sell actions, target prices, or return promises.
- Do not treat retrieved text as ground truth without source, chunk id, matched terms, and limitations.
- Keep every output mock-first, deterministic, observable, and testable without real keys.

## Required Output

- `retrieval_trace`
- `retrieved_context`
- `candidate_evidence`
- `augmented_evidence` or equivalent context references
- `risk_disclosure`
- `next_lab: Lab 05 User Preference Memory`

## Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 04-research-rag-basic
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```
