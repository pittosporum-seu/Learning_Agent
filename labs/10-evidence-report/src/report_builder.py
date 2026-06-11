from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evidence_collector import collect_report_inputs
from report_model import DEFAULT_GENERATED_AT, ReportSection, make_report_id, sanitize_text


LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_PATH = LAB_ROOT / "data" / "report_template.json"


def load_report_template(path: Path | None = None) -> dict[str, Any]:
    template_path = path or DEFAULT_TEMPLATE_PATH
    return json.loads(template_path.read_text(encoding="utf-8"))


def build_report_from_planner(
    planner_output: dict[str, Any],
    generated_at: str | None = None,
    template: dict[str, Any] | None = None,
) -> dict[str, Any]:
    template = template or load_report_template()
    inputs = collect_report_inputs(planner_output)
    generated_at = generated_at or DEFAULT_GENERATED_AT
    report_status = resolve_report_status(inputs["planner_status"])
    report_id = make_report_id(inputs["request"], inputs["user_id"])

    sections = build_sections(report_id, generated_at, report_status, inputs)
    report_generation_trace = build_report_generation_trace(sections, inputs, report_status)
    evidence_report = {
        "report_id": report_id,
        "status": report_status,
        "template_id": template.get("template_id", ""),
        "human_review_required": True,
        "sections": {section["section_id"]: section for section in sections},
        "evidence_refs": inputs["evidence_refs"],
        "risk_and_limitations": sections[6]["content"],
        "human_review_checklist": sections[7]["content"],
    }
    final_output = build_final_output(evidence_report, inputs)
    return {
        "status": report_status,
        "evidence_report": evidence_report,
        "report_generation_trace": report_generation_trace,
        "evidence_refs": inputs["evidence_refs"],
        "risk_disclosure": inputs["risk_disclosure"],
        "human_review_required": True,
        "final_output": final_output,
        "next_lab": "Lab 11 Simulation Portfolio",
    }


def resolve_report_status(planner_status: str) -> str:
    if planner_status == "blocked":
        return "blocked"
    return "needs_human_review"


def build_sections(report_id: str, generated_at: str, report_status: str, inputs: dict[str, Any]) -> list[dict[str, Any]]:
    strategy_spec = inputs["strategy_spec"]
    evidence_refs = [item["evidence_id"] for item in inputs["evidence_refs"]]
    report_header = {
        "report_id": report_id,
        "generated_at": generated_at,
        "source_lab": "Lab 09 Research Planner DAG",
        "status": report_status,
        "human_review_required": True,
    }
    strategy_summary = {
        "original_request": sanitize_text(inputs["request"]),
        "themes": strategy_spec.get("themes", []),
        "horizon_days": strategy_spec.get("horizon_days"),
        "routing_mode": strategy_spec.get("routing_decision", {}).get("mode", strategy_spec.get("execution_mode", "")),
        "output_type": sanitize_text(strategy_spec.get("output", "")),
    }
    planner_summary = {
        "planner_status": inputs["planner_status"],
        "completed_nodes": [
            node.get("node_id")
            for node in inputs["research_dag"]
            if node.get("status") == "completed"
        ],
        "blocked_nodes": [
            {"node_id": node.get("node_id"), "reason": node.get("blocked_reason") or node.get("reason", "")}
            for node in inputs["blocked_nodes"]
        ],
        "skipped_nodes": [
            {"node_id": node.get("node_id"), "reason": node.get("skipped_reason", "")}
            for node in inputs["skipped_nodes"]
        ],
        "waiting_human_confirmation_nodes": [
            {
                "node_id": node.get("node_id"),
                "required_confirmations": node.get("produced_outputs", {}).get("required_confirmations", []),
            }
            for node in inputs["waiting_human_confirmation_nodes"]
        ],
    }
    risk_and_limitations = {
        "risk_disclosure": inputs["risk_disclosure"],
        "mock_data_notice": "This report is built from deterministic mock data and local trace summaries.",
        "evidence_gaps": inputs["evidence_gaps"],
        "uncertainty_notes": [
            "Evidence quality is mock-only and cannot be used as a live market conclusion.",
            "Human review is required before any watchlist, simulation, skill activation, or publication handoff.",
        ],
        "no_investment_advice": "This report is for Agent learning and research workflow demonstration only.",
    }
    human_review_checklist = {
        "required": True,
        "review_evidence_sources": True,
        "confirm_no_trading_action": True,
        "confirm_risk_disclosure": bool(inputs["risk_disclosure"]),
        "confirm_before_watchlist_simulation_or_publication": True,
        "items": [
            "Review every evidence source and limitation.",
            "Confirm that no trading action is present.",
            "Confirm the risk disclosure is visible.",
            "Confirm before watchlist, simulation, skill activation, or publication handoff.",
        ],
        "blocked_until_reviewed": [
            "watchlist handoff",
            "simulation handoff",
            "skill activation",
            "external publication",
        ],
        "review_reason": "The planner stopped at a human review boundary or returned a blocked state.",
    }
    next_steps = {
        "next_lab": "Lab 11 Simulation Portfolio",
        "allowed_next_steps": [
            "Review the draft report.",
            "Fill evidence gaps with additional sourced mock evidence.",
            "Proceed to simulation design only after human review.",
        ],
        "not_allowed_actions": [
            "unreviewed publication",
            "automatic watchlist handoff",
            "automatic simulation handoff",
            "automatic skill activation",
        ],
    }

    section_defs = [
        ("report_header", "Report Header", report_header, []),
        ("strategy_summary", "Strategy Summary", strategy_summary, []),
        ("planner_summary", "Planner Summary", planner_summary, [ref for ref in evidence_refs if ref.startswith("planner-")]),
        (
            "candidate_observation_pool",
            "Candidate Observation Pool",
            inputs["candidate_observations"],
            sorted({ref for item in inputs["candidate_observations"] for ref in item.get("evidence_refs", [])}),
        ),
        ("evidence_table", "Evidence Table", inputs["evidence_refs"], evidence_refs),
        (
            "retrieved_context_table",
            "Retrieved Context Table",
            inputs["retrieved_context_table"],
            [ref for ref in evidence_refs if ref.startswith("context-")],
        ),
        ("risk_and_limitations", "Risk and Limitations", risk_and_limitations, []),
        ("human_review_checklist", "Human Review Checklist", human_review_checklist, []),
        ("next_steps", "Next Steps", next_steps, []),
    ]

    sections: list[dict[str, Any]] = []
    for section_id, title, content, refs in section_defs:
        section_status = section_status_for(section_id, content, report_status)
        sections.append(
            ReportSection(
                section_id=section_id,
                title=title,
                status=section_status,
                content=content,
                evidence_refs=refs,
                limitations=section_limitations(section_id, report_status, inputs),
            ).to_dict()
        )
    return sections


def section_status_for(section_id: str, content: Any, report_status: str) -> str:
    if report_status == "blocked" and section_id in {"candidate_observation_pool", "retrieved_context_table"} and not content:
        return "blocked"
    if section_id == "evidence_table" and not content:
        return "degraded"
    if section_id == "candidate_observation_pool" and not content:
        return "degraded"
    return "ready"


def section_limitations(section_id: str, report_status: str, inputs: dict[str, Any]) -> list[str]:
    limitations: list[str] = []
    if report_status == "blocked":
        limitations.append("Planner was blocked, so this section may contain only gap or status information.")
    if section_id == "candidate_observation_pool" and not inputs["candidate_observations"]:
        limitations.append("No candidate observations are available.")
    if section_id == "evidence_table":
        limitations.append("All evidence is mock or local trace data.")
    return limitations


def build_report_generation_trace(
    sections: list[dict[str, Any]],
    inputs: dict[str, Any],
    report_status: str,
) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = []
    source_map = {
        "report_header": ["planner_output"],
        "strategy_summary": ["planner_output.strategy_spec"],
        "planner_summary": ["planner_output.research_dag", "planner_output.planner_trace"],
        "candidate_observation_pool": ["candidate_evidence", "preference_adjusted_evidence"],
        "evidence_table": ["adapter_trace", "candidate_evidence", "retrieved_context", "planner_trace"],
        "retrieved_context_table": ["retrieved_context"],
        "risk_and_limitations": ["risk_disclosure", "blocked_nodes", "skipped_nodes"],
        "human_review_checklist": ["waiting_human_confirmation_nodes", "risk_disclosure"],
        "next_steps": ["planner_output.final_output"],
    }
    for section in sections:
        section_id = section["section_id"]
        warning = ""
        status = "completed" if section["status"] == "ready" else section["status"]
        if report_status == "blocked":
            warning = "planner status blocked; report is limited to sourced status and evidence gaps"
        elif section_id == "risk_and_limitations" and inputs["evidence_gaps"]:
            warning = "evidence gaps were recorded"
        trace.append(
            {
                "step": f"build_{section_id}",
                "status": status,
                "input_sources": source_map.get(section_id, ["planner_output"]),
                "output_section": section_id,
                "evidence_refs": section.get("evidence_refs", []),
                "warning_or_gap": warning,
            }
        )
    return trace


def build_final_output(evidence_report: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    candidate_pool = evidence_report["sections"]["candidate_observation_pool"]["content"]
    return {
        "summary": (
            "Evidence Report draft is ready for human review."
            if evidence_report["status"] == "needs_human_review"
            else "Evidence Report is blocked and only records sourced gaps."
        ),
        "report_status": evidence_report["status"],
        "candidate_observation_count": len(candidate_pool),
        "evidence_ref_count": len(evidence_report["evidence_refs"]),
        "evidence_gaps": inputs["evidence_gaps"],
        "allowed_next_steps": evidence_report["sections"]["next_steps"]["content"]["allowed_next_steps"],
        "not_allowed_actions": evidence_report["sections"]["next_steps"]["content"]["not_allowed_actions"],
        "next_lab": "Lab 11 Simulation Portfolio",
        "risk_disclosure": inputs["risk_disclosure"],
    }
