from __future__ import annotations

from typing import Any

from document_loader import load_documents
from simple_retriever import retrieve


def build_retrieval_query(strategy_spec: dict[str, Any], candidate_evidence: list[dict[str, Any]]) -> str:
    routing = strategy_spec.get("routing_decision") or {}
    risk_flags = sorted(
        {
            flag
            for candidate in candidate_evidence
            for flag in candidate.get("risk_flags", [])
        }
    )
    evidence_terms = sorted(
        {
            evidence_item.get("source_type", "")
            for candidate in candidate_evidence
            for evidence_item in candidate.get("evidence_items", [])
            if evidence_item.get("source_type")
        }
    )
    parts = [
        strategy_spec.get("original_request", ""),
        " ".join(strategy_spec.get("themes", [])),
        " ".join(strategy_spec.get("candidate_rules", [])),
        " ".join(strategy_spec.get("risk_filters", [])),
        strategy_spec.get("output", ""),
        strategy_spec.get("execution_mode", ""),
        routing.get("mode", ""),
        " ".join(risk_flags),
        " ".join(evidence_terms),
        "candidate_evidence retrieved_context report_template risk_disclosure risk_filters",
    ]
    return " ".join(part for part in parts if part).strip()


def build_rag_context(
    strategy_spec: dict[str, Any],
    candidate_evidence: list[dict[str, Any]],
    top_k: int = 5,
    chunks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    document_chunks = chunks if chunks is not None else load_documents()
    query = build_retrieval_query(strategy_spec, candidate_evidence)
    retrieved = retrieve(query=query, chunks=document_chunks, top_k=top_k)
    retrieved_context = [
        {
            "source": item["source"],
            "chunk_id": item["chunk_id"],
            "section": item["section"],
            "content": item["content"],
            "matched_terms": item["matched_terms"],
            "score": item["score"],
            "used_for": classify_context_use(item),
        }
        for item in retrieved
    ]
    retrieval_trace = [
        {
            "step": "build_query",
            "status": "completed",
            "query": query,
            "candidate_evidence_count": len(candidate_evidence),
            "document_chunk_count": len(document_chunks),
        },
        {
            "step": "retrieve_context",
            "status": "completed",
            "top_k": top_k,
            "matched_count": len(retrieved_context),
            "selected_chunks": [
                {
                    "source": item["source"],
                    "chunk_id": item["chunk_id"],
                    "score": item["score"],
                    "matched_terms": item["matched_terms"],
                    "used_for": classify_context_use(item),
                }
                for item in retrieved
            ],
        },
    ]
    return {
        "retrieval_trace": retrieval_trace,
        "retrieved_context": retrieved_context,
        "augmented_evidence": attach_context_refs(candidate_evidence, retrieved_context),
    }


def classify_context_use(context_item: dict[str, Any]) -> str:
    source = context_item.get("source", "")
    if source == "risk_policy.md":
        return "risk_boundary"
    if source == "report_template.md":
        return "report_structure"
    if source == "strategy_policy.md":
        return "strategy_rule"
    return "background_context"


def attach_context_refs(
    candidate_evidence: list[dict[str, Any]],
    retrieved_context: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    context_refs = [
        {
            "source": item["source"],
            "chunk_id": item["chunk_id"],
            "used_for": item["used_for"],
        }
        for item in retrieved_context
    ]
    return [
        {
            **candidate,
            "retrieved_context_refs": context_refs,
        }
        for candidate in candidate_evidence
    ]
