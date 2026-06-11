from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}
PROHIBITED_SEMANTIC_PATTERNS = [
    "稳赚",
    "必涨",
    "保证收益",
    "自动买入",
    "自动卖出",
    "certain profit",
    "guaranteed return",
]
ALLOWED_REPORT_STATUSES = {"draft", "needs_human_review", "blocked"}
DEFAULT_GENERATED_AT = "2026-06-11T00:00:00Z"


@dataclass
class EvidenceReference:
    evidence_id: str
    source_type: str
    source_name: str
    source_path: str
    claim: str
    value_summary: str
    limitations: str
    confidence: str = "mock"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReportSection:
    section_id: str
    title: str
    status: str
    content: Any
    evidence_refs: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def contains_prohibited_output_key(value: Any) -> bool:
    return bool(find_prohibited_output_key_paths(value))


def find_prohibited_output_key_paths(value: Any, path: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in PROHIBITED_OUTPUT_KEYS:
                paths.append(child_path)
            paths.extend(find_prohibited_output_key_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(find_prohibited_output_key_paths(child, f"{path}[{index}]"))
    return paths


def find_prohibited_semantic_paths(value: Any, path: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        if any(pattern.lower() in lowered for pattern in PROHIBITED_SEMANTIC_PATTERNS):
            paths.append(path)
    elif isinstance(value, dict):
        for key, child in value.items():
            paths.extend(find_prohibited_semantic_paths(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(find_prohibited_semantic_paths(child, f"{path}[{index}]"))
    return paths


def sanitize_text(text: Any) -> str:
    value = "" if text is None else str(text)
    for pattern in PROHIBITED_SEMANTIC_PATTERNS:
        value = value.replace(pattern, "[redacted_prohibited_semantic]")
    for pattern in PROHIBITED_OUTPUT_KEYS:
        value = value.replace(pattern, "[redacted_prohibited_field]")
    return value


def summarize_value(value: Any, max_length: int = 220) -> str:
    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        rendered = "" if value is None else str(value)
    rendered = sanitize_text(rendered)
    if len(rendered) <= max_length:
        return rendered
    return f"{rendered[: max_length - 3]}..."


def make_report_id(request_text: str, user_id: str) -> str:
    import hashlib

    digest = hashlib.sha1(f"{request_text}|{user_id}".encode("utf-8")).hexdigest()[:10]
    return f"mock-evidence-report-{digest}"
