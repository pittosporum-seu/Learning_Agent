from __future__ import annotations

import re
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = LAB_ROOT / "data"

KEYWORD_CANDIDATES = [
    "StrategySpec",
    "strategy",
    "market",
    "theme",
    "horizon",
    "candidate_rules",
    "risk_filters",
    "execution_mode",
    "workflow",
    "agent",
    "candidate_evidence",
    "evidence",
    "mock_source",
    "candidate_id",
    "claim",
    "confidence",
    "limitations",
    "tool_trace",
    "insufficient_evidence",
    "evidence_gap",
    "mock",
    "RAG",
    "retrieved_context",
    "risk_disclosure",
    "not_investment_advice",
    "observation_pool",
    "no_return_promise",
    "negative_news",
    "risk_flags",
    "guardrail",
    "uncertainty",
    "human_confirmation",
    "watchlist",
    "simulation_portfolio",
    "skill_activation",
    "real_provider",
    "report_template",
    "request_summary",
    "strategy_rules",
    "source",
    "chunk_id",
    "section",
    "matched_terms",
    "used_for",
    "citation",
    "next_lab",
    "user_preference_memory",
    "memory",
    "filters",
    "report_style",
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


def load_documents(data_dir: Path | None = None) -> list[dict[str, Any]]:
    base_dir = data_dir or DATA_DIR
    chunks: list[dict[str, Any]] = []
    for markdown_path in sorted(base_dir.glob("*.md")):
        chunks.extend(load_markdown_chunks(markdown_path))
    return chunks


def load_markdown_chunks(markdown_path: Path) -> list[dict[str, Any]]:
    text = markdown_path.read_text(encoding="utf-8")
    sections = split_markdown_sections(text)
    chunks: list[dict[str, Any]] = []
    for index, section in enumerate(sections, start=1):
        content = section["content"].strip()
        if not content:
            continue
        chunk_id = f"{markdown_path.stem}-{index:02d}"
        chunks.append(
            {
                "chunk_id": chunk_id,
                "source": markdown_path.name,
                "section": section["title"],
                "content": content,
                "keywords": extract_keywords(content),
            }
        )
    return chunks


def split_markdown_sections(text: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_title = "Document"
    current_lines: list[str] = []

    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            if current_lines:
                sections.append({"title": current_title, "content": "\n".join(current_lines)})
                current_lines = []
            current_title = heading.group(2).strip()
            continue
        current_lines.append(line)

    if current_lines:
        sections.append({"title": current_title, "content": "\n".join(current_lines)})

    normalized: list[dict[str, str]] = []
    for section in sections:
        paragraphs = [item.strip() for item in re.split(r"\n\s*\n", section["content"]) if item.strip()]
        if len(paragraphs) <= 1:
            normalized.append(section)
            continue
        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            title = section["title"] if paragraph_index == 1 else f"{section['title']} ({paragraph_index})"
            normalized.append({"title": title, "content": paragraph})
    return normalized


def extract_keywords(content: str) -> list[str]:
    lowered = content.lower()
    keywords = {
        candidate
        for candidate in KEYWORD_CANDIDATES
        if candidate.lower() in lowered or candidate in content
    }
    keywords.update(re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", content))
    return sorted(keywords, key=lambda item: item.lower())
