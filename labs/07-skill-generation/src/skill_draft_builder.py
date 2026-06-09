from __future__ import annotations

from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = LAB_ROOT / "data" / "skill_draft_template.md"


def build_skill_draft(skill_registry_output: dict[str, Any]) -> dict[str, Any]:
    selected_skill = choose_draft_source_skill(skill_registry_output)
    registered_skill = find_registered_skill(skill_registry_output, selected_skill["name"])
    trace_event = find_trace_event(skill_registry_output, selected_skill["name"])
    risk_disclosure = skill_registry_output.get("risk_disclosure", "")

    generated_skill_draft = {
        "name": f"{selected_skill['name']}-draft",
        "draft": True,
        "source_skill": selected_skill["name"],
        "description": build_description(selected_skill),
        "trigger_scenarios": build_trigger_scenarios(selected_skill, trace_event),
        "disabled_scenarios": build_disabled_scenarios(registered_skill, skill_registry_output),
        "inputs": list(registered_skill.get("inputs", selected_skill.get("inputs", []))),
        "outputs": list(registered_skill.get("outputs", selected_skill.get("outputs", []))),
        "workflow_steps": build_workflow_steps(selected_skill),
        "human_confirmation_points": build_human_confirmation_points(selected_skill),
        "safety_boundaries": build_safety_boundaries(risk_disclosure),
        "test_cases": build_test_cases(selected_skill),
        "risk_disclosure": risk_disclosure,
        "review_status": "draft_requires_human_review",
    }
    return {
        "generated_skill_draft": generated_skill_draft,
        "skill_draft_markdown": render_skill_draft_markdown(generated_skill_draft),
    }


def choose_draft_source_skill(skill_registry_output: dict[str, Any]) -> dict[str, Any]:
    selected_skills = skill_registry_output.get("selected_skills", [])
    if not selected_skills:
        raise ValueError("No selected mock Skill is available for draft generation.")

    for skill in selected_skills:
        if skill.get("name") == "candidate-evidence-summary":
            return skill
    return selected_skills[0]


def find_registered_skill(skill_registry_output: dict[str, Any], skill_name: str) -> dict[str, Any]:
    for skill in skill_registry_output.get("registered_skills", []):
        if skill.get("name") == skill_name:
            return skill
    return {}


def find_trace_event(skill_registry_output: dict[str, Any], skill_name: str) -> dict[str, Any]:
    for event in skill_registry_output.get("skill_selection_trace", []):
        if event.get("skill_name") == skill_name:
            return event
    return {}


def build_description(selected_skill: dict[str, Any]) -> str:
    return (
        f"Draft Skill based on `{selected_skill['name']}`. "
        "It summarizes mock evidence with source awareness and keeps finance output inside teaching boundaries."
    )


def build_trigger_scenarios(selected_skill: dict[str, Any], trace_event: dict[str, Any]) -> list[str]:
    matched = trace_event.get("matched_triggers") or selected_skill.get("matched_triggers", [])
    scenarios = [
        "A completed mock investment research flow has structured candidate evidence.",
        "The output needs a source-aware observation-pool brief for learning review.",
        "A risk disclosure is present and the upstream registry selected this analysis Skill.",
    ]
    if matched:
        scenarios.append(f"Matched registry triggers: {', '.join(matched)}.")
    return scenarios


def build_disabled_scenarios(registered_skill: dict[str, Any], skill_registry_output: dict[str, Any]) -> list[str]:
    disabled = list(registered_skill.get("disabled_when", []))
    disabled.extend(
        [
            "upstream_status_is_not_completed",
            "candidate_evidence_is_missing",
            "risk_disclosure_is_missing",
            "human_review_has_not_approved_formal_activation",
            "request_asks_for_automatic_trading_or_certain_price_movement",
        ]
    )
    if skill_registry_output.get("status") != "completed":
        disabled.append("current_upstream_output_is_blocked")
    return dedupe(disabled)


def build_workflow_steps(selected_skill: dict[str, Any]) -> list[str]:
    return [
        "Read StrategySpec, candidate_evidence, retrieved_context, and risk_disclosure from upstream Lab output.",
        "Verify the upstream registry selected the source mock Skill and did not report blocking guardrails.",
        "Summarize only evidence-backed observations and preserve source references.",
        "List limitations and uncertainty before any handoff to later Labs.",
        "Return a draft output for human review without enabling any runtime Skill.",
    ]


def build_human_confirmation_points(selected_skill: dict[str, Any]) -> list[str]:
    points = ["Human review is required before converting this draft into a formal Skill."]
    if selected_skill.get("requires_human_confirmation"):
        points.append("Human confirmation is required before using the source Skill output in any handoff.")
    points.append("Human confirmation is required before any watchlist, simulation portfolio, or published report action.")
    return points


def build_safety_boundaries(risk_disclosure: str) -> list[str]:
    return [
        "Keep the output as a learning demo and observation-pool evidence summary only.",
        "Do not call real model, vector database, finance, account, watchlist, or portfolio APIs.",
        "Do not write generated drafts into .agents/ or .codex/ runtime directories.",
        "Do not auto-enable the draft; it remains pending human review.",
        "Do not provide investment advice, certain price movement claims, trading actions, or target prices.",
        f"Required risk_disclosure: {risk_disclosure}",
    ]


def build_test_cases(selected_skill: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "case_id": "normal_completed_flow",
            "input": "Completed Lab 06 output with selected mock analysis Skill and risk_disclosure.",
            "expected": "Draft is generated and review status remains needs_human_review.",
        },
        {
            "case_id": "blocked_upstream_flow",
            "input": "Blocked Lab 06 output.",
            "expected": "No activatable Skill is generated.",
        },
        {
            "case_id": "missing_risk_disclosure",
            "input": "Draft without risk_disclosure.",
            "expected": "Safety review fails and requires manual correction.",
        },
    ]


def render_skill_draft_markdown(generated_skill_draft: dict[str, Any]) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "name": generated_skill_draft["name"],
        "description": generated_skill_draft["description"],
        "trigger_scenarios": render_list(generated_skill_draft["trigger_scenarios"]),
        "disabled_scenarios": render_list(generated_skill_draft["disabled_scenarios"]),
        "inputs": render_list(generated_skill_draft["inputs"]),
        "outputs": render_list(generated_skill_draft["outputs"]),
        "workflow_steps": render_list(generated_skill_draft["workflow_steps"], numbered=True),
        "human_confirmation_points": render_list(generated_skill_draft["human_confirmation_points"]),
        "safety_boundaries": render_list(generated_skill_draft["safety_boundaries"]),
        "test_cases": render_test_cases(generated_skill_draft["test_cases"]),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{ " + key + " }}", value)
    return rendered


def render_list(items: list[str], numbered: bool = False) -> str:
    if numbered:
        return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))
    return "\n".join(f"- {item}" for item in items)


def render_test_cases(test_cases: list[dict[str, str]]) -> str:
    lines = ["| Case | Input | Expected |", "| --- | --- | --- |"]
    for case in test_cases:
        lines.append(f"| {case['case_id']} | {case['input']} | {case['expected']} |")
    return "\n".join(lines)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
