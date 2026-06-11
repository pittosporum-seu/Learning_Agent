from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dag_model import ResearchDagNode, validate_dag_dependencies


LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_PATH = LAB_ROOT / "data" / "planner_template.json"

REQUIRED_NODE_IDS = [
    "parse_and_route",
    "adapter_capability_check",
    "candidate_generation",
    "market_data_check",
    "news_risk_check",
    "evidence_context_attach",
    "memory_preference_adjustment",
    "skill_selection",
    "human_review_gate",
]


def load_planner_template(template_path: Path | None = None) -> dict[str, Any]:
    path = template_path or DEFAULT_TEMPLATE_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def build_research_dag(adapter_output: dict[str, Any], template_path: Path | None = None) -> list[ResearchDagNode]:
    template = load_planner_template(template_path)
    nodes = [ResearchDagNode.from_dict(item) for item in template.get("nodes", [])]
    node_ids = [node.node_id for node in nodes]
    missing = [node_id for node_id in REQUIRED_NODE_IDS if node_id not in node_ids]
    if missing:
        raise ValueError(f"Planner template missing required nodes: {missing}")

    adapter_context = build_adapter_context(adapter_output)
    for node in nodes:
        node.context = {
            "adapter_mode": adapter_context["adapter_mode"],
            "provider_mode": adapter_context["provider_mode"],
            "adapter_status": adapter_context["adapter_status"],
            "adapter_trace_count": adapter_context["adapter_trace_count"],
            "safety_gate": adapter_context["safety_gate"],
            "risk_disclosure_present": adapter_context["risk_disclosure_present"],
            "skill_generation_status": adapter_context["skill_generation_status"],
        }
    validate_dag_dependencies(nodes)
    return nodes


def build_adapter_context(adapter_output: dict[str, Any]) -> dict[str, Any]:
    skill_generation_output = adapter_output.get("skill_generation_output", {})
    return {
        "adapter_status": adapter_output.get("status", "unknown"),
        "adapter_mode": adapter_output.get("adapter_mode", "unknown"),
        "provider_mode": adapter_output.get("provider_mode", "unknown"),
        "safety_gate": adapter_output.get("safety_gate", {}),
        "adapter_trace_count": len(adapter_output.get("adapter_trace", [])),
        "risk_disclosure_present": bool(adapter_output.get("risk_disclosure")),
        "skill_generation_status": skill_generation_output.get("status", "unknown"),
    }
