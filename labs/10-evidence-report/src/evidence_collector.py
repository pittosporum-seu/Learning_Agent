from __future__ import annotations

from typing import Any

from report_model import EvidenceReference, sanitize_text, summarize_value


def collect_report_inputs(planner_output: dict[str, Any]) -> dict[str, Any]:
    adapter_output = planner_output.get("adapter_output", {})
    skill_generation_output = adapter_output.get("skill_generation_output", {})
    skill_registry_output = skill_generation_output.get("skill_registry_output", {})
    memory_output = skill_registry_output.get("memory_output", {})
    rag_output = memory_output.get("rag_output", {})

    candidate_evidence = rag_output.get("candidate_evidence", [])
    retrieved_context = rag_output.get("retrieved_context", [])
    preference_adjusted_evidence = memory_output.get("preference_adjusted_evidence", [])
    strategy_spec = rag_output.get("strategy_spec", {})
    references = build_evidence_references(planner_output, candidate_evidence, retrieved_context)

    return {
        "request": planner_output.get("request", adapter_output.get("request", "")),
        "user_id": planner_output.get("user_id", adapter_output.get("user_id", "")),
        "strategy_spec": strategy_spec,
        "adapter_trace": adapter_output.get("adapter_trace", []),
        "candidate_evidence": candidate_evidence,
        "retrieved_context": retrieved_context,
        "preference_adjusted_evidence": preference_adjusted_evidence,
        "planner_trace": planner_output.get("planner_trace", []),
        "research_dag": planner_output.get("research_dag", []),
        "blocked_nodes": planner_output.get("blocked_nodes", []),
        "skipped_nodes": planner_output.get("skipped_nodes", []),
        "waiting_human_confirmation_nodes": planner_output.get("waiting_human_confirmation_nodes", []),
        "planner_status": planner_output.get("status", "blocked"),
        "risk_disclosure": planner_output.get("risk_disclosure", adapter_output.get("risk_disclosure", "")),
        "evidence_refs": references,
        "candidate_observations": build_candidate_observations(candidate_evidence, preference_adjusted_evidence),
        "retrieved_context_table": build_retrieved_context_table(retrieved_context),
        "evidence_gaps": build_evidence_gaps(planner_output),
    }


def build_evidence_references(
    planner_output: dict[str, Any],
    candidate_evidence: list[dict[str, Any]],
    retrieved_context: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    references: list[EvidenceReference] = []

    for candidate_index, candidate in enumerate(candidate_evidence):
        for evidence_index, item in enumerate(candidate.get("evidence_items", [])):
            evidence_id = item.get("evidence_id") or f"{candidate.get('candidate_id', 'candidate')}-evidence-{evidence_index}"
            references.append(
                EvidenceReference(
                    evidence_id=evidence_id,
                    source_type=item.get("source_type", "candidate_evidence"),
                    source_name=item.get("source_name", "candidate_evidence"),
                    source_path=(
                        "planner_output.adapter_output.skill_generation_output.skill_registry_output."
                        f"memory_output.rag_output.candidate_evidence[{candidate_index}].evidence_items[{evidence_index}]"
                    ),
                    claim=sanitize_text(item.get("claim", "")),
                    value_summary=summarize_value(item.get("value", "")),
                    limitations=sanitize_text(item.get("limitations", "")),
                    confidence=item.get("confidence", "mock"),
                )
            )

    for index, item in enumerate(retrieved_context):
        chunk_id = item.get("chunk_id", f"context-{index}")
        references.append(
            EvidenceReference(
                evidence_id=f"context-{chunk_id}",
                source_type="retrieved_context",
                source_name=item.get("source", "retrieved_context"),
                source_path=(
                    "planner_output.adapter_output.skill_generation_output.skill_registry_output."
                    f"memory_output.rag_output.retrieved_context[{index}]"
                ),
                claim=f"Retrieved context used for {sanitize_text(item.get('used_for', 'unknown'))}.",
                value_summary=summarize_value(item.get("content", "")),
                limitations="Local mock markdown chunk; not a live external source.",
                confidence="mock",
            )
        )

    adapter_output = planner_output.get("adapter_output", {})
    for index, event in enumerate(adapter_output.get("adapter_trace", [])):
        capability = event.get("capability", f"capability-{index}")
        references.append(
            EvidenceReference(
                evidence_id=f"adapter-{capability}-{index}",
                source_type="adapter_trace",
                source_name=event.get("adapter_name", "adapter"),
                source_path=f"planner_output.adapter_output.adapter_trace[{index}]",
                claim=f"Adapter capability {capability} ended with status {event.get('status', 'unknown')}.",
                value_summary=summarize_value(event.get("output", {})),
                limitations="Adapter result is a mock or gated local integration summary.",
                confidence="mock",
            )
        )

    for index, event in enumerate(planner_output.get("planner_trace", [])):
        node_id = event.get("node_id", f"node-{index}")
        references.append(
            EvidenceReference(
                evidence_id=f"planner-{node_id}-{index}",
                source_type="planner_trace",
                source_name="Lab 09 planner_trace",
                source_path=f"planner_output.planner_trace[{index}]",
                claim=f"Planner node {node_id} ended with status {event.get('status', 'unknown')}.",
                value_summary=summarize_value(
                    {
                        "reason": event.get("reason", ""),
                        "produced_outputs": event.get("produced_outputs", {}),
                        "blocked_reason": event.get("blocked_reason", ""),
                        "skipped_reason": event.get("skipped_reason", ""),
                    }
                ),
                limitations="Planner trace is deterministic Lab 09 output, not live market evidence.",
                confidence="mock",
            )
        )

    return [item.to_dict() for item in references]


def build_candidate_observations(
    candidate_evidence: list[dict[str, Any]],
    preference_adjusted_evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    adjusted_ids = {item.get("candidate_id") for item in preference_adjusted_evidence}
    adjusted_known = bool(preference_adjusted_evidence)
    observations: list[dict[str, Any]] = []

    for candidate in candidate_evidence:
        evidence_refs = [
            item.get("evidence_id")
            for item in candidate.get("evidence_items", [])
            if item.get("evidence_id")
        ]
        candidate_id = candidate.get("candidate_id", "")
        preference_status = "included_in_adjusted_view"
        if adjusted_known and candidate_id not in adjusted_ids:
            preference_status = "filtered_from_adjusted_view"
        observations.append(
            {
                "candidate_id": candidate_id,
                "candidate_name": sanitize_text(candidate.get("candidate_name", "")),
                "theme": sanitize_text(candidate.get("theme", "")),
                "observation_summary": "Mock candidate observation assembled from sourced evidence.",
                "evidence_refs": evidence_refs,
                "risk_flags": candidate.get("risk_flags", []),
                "preference_status": preference_status,
            }
        )

    return observations


def build_retrieved_context_table(retrieved_context: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table: list[dict[str, Any]] = []
    for item in retrieved_context:
        table.append(
            {
                "source": item.get("source", ""),
                "chunk_id": item.get("chunk_id", ""),
                "section": sanitize_text(item.get("section", "")),
                "used_for": sanitize_text(item.get("used_for", "")),
                "matched_terms": item.get("matched_terms", []),
            }
        )
    return table


def build_evidence_gaps(planner_output: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    if planner_output.get("status") == "blocked":
        gaps.append("Planner output is blocked, so the report cannot produce normal candidate observations.")

    for node in planner_output.get("blocked_nodes", []):
        node_id = node.get("node_id", "unknown")
        reason = node.get("blocked_reason") or node.get("reason", "blocked")
        gaps.append(f"Node {node_id} blocked: {sanitize_text(reason)}")

    for node in planner_output.get("skipped_nodes", []):
        node_id = node.get("node_id", "unknown")
        reason = node.get("skipped_reason", "skipped")
        gaps.append(f"Node {node_id} skipped: {sanitize_text(reason)}")

    if not planner_output.get("adapter_output", {}).get("adapter_trace"):
        gaps.append("No adapter_trace items are available for evidence table adapter references.")

    return gaps
