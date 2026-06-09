# Strategy Policy

## StrategySpec completeness

A strategy request should preserve the original natural-language request and extract market, themes, horizon, candidate rules, risk filters, expected output, and execution mode.

Keywords: StrategySpec, strategy, market, theme, horizon, candidate_rules, risk_filters, execution_mode, observation_pool, workflow, agent

## Candidate evidence handoff

Tool results from Lab 03 must be converted into evidence before any report step. Evidence should keep the mock source, candidate id, claim, value, confidence, and limitations.

Keywords: candidate_evidence, evidence, mock_source, candidate_id, claim, confidence, limitations, tool_trace

## Evidence gaps

If a query asks for information that is not present in the mock knowledge base, the output should state that evidence is insufficient instead of filling the gap with model assumptions.

Keywords: insufficient_evidence, evidence_gap, mock, RAG, retrieved_context
