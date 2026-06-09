from __future__ import annotations

import re
from typing import Any


EXTRA_QUERY_TERMS = [
    "StrategySpec",
    "candidate_evidence",
    "retrieved_context",
    "risk_disclosure",
    "risk_filters",
    "risk_flags",
    "report_template",
    "source",
    "chunk_id",
    "matched_terms",
    "used_for",
    "电网设备",
    "趋势",
    "回撤",
    "负面新闻",
    "风险",
    "观察池",
    "报告",
    "模板",
    "证据",
]


def retrieve(query: str, chunks: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    query_terms = tokenize_query(query)
    scored: list[dict[str, Any]] = []
    for chunk in chunks:
        matched_terms = match_terms(query_terms, chunk)
        if not matched_terms:
            continue
        score = score_chunk(matched_terms, chunk)
        scored.append(
            {
                **chunk,
                "matched_terms": matched_terms,
                "score": score,
            }
        )

    return sorted(scored, key=lambda item: (-item["score"], item["source"], item["chunk_id"]))[:top_k]


def tokenize_query(query: str) -> list[str]:
    terms = set(re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", query))
    for candidate in EXTRA_QUERY_TERMS:
        if candidate.lower() in query.lower() or candidate in query:
            terms.add(candidate)
    return sorted(terms, key=lambda item: item.lower())


def match_terms(query_terms: list[str], chunk: dict[str, Any]) -> list[str]:
    content = chunk.get("content", "")
    lowered_content = content.lower()
    keywords = {keyword.lower(): keyword for keyword in chunk.get("keywords", [])}
    matched: set[str] = set()

    for term in query_terms:
        lowered_term = term.lower()
        if lowered_term in keywords:
            matched.add(keywords[lowered_term])
        elif lowered_term in lowered_content or term in content:
            matched.add(term)

    return sorted(matched, key=lambda item: item.lower())


def score_chunk(matched_terms: list[str], chunk: dict[str, Any]) -> float:
    keyword_matches = sum(1 for term in matched_terms if term in chunk.get("keywords", []))
    return float(len(matched_terms) + keyword_matches * 0.5)
