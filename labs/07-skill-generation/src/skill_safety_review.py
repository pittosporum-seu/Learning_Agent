from __future__ import annotations

from typing import Any


PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def review_skill_draft(generated_skill_draft: dict[str, Any], skill_draft_markdown: str) -> dict[str, Any]:
    issues: list[str] = []
    if not generated_skill_draft:
        issues.append("missing_draft")
    if not generated_skill_draft.get("risk_disclosure"):
        issues.append("missing_risk_disclosure")
    if not generated_skill_draft.get("disabled_scenarios"):
        issues.append("missing_disabled_scenarios")
    if not has_human_review_boundary(generated_skill_draft, skill_draft_markdown):
        issues.append("missing_human_review_or_confirmation")
    if contains_prohibited_output_keys(generated_skill_draft):
        issues.append("prohibited_output_key_present")
    if "DRAFT" not in skill_draft_markdown:
        issues.append("missing_draft_marker")

    status = "failed" if issues else "needs_human_review"
    return {
        "status": status,
        "issues": issues,
        "required_human_actions": build_required_human_actions(status, issues),
    }


def has_human_review_boundary(generated_skill_draft: dict[str, Any], skill_draft_markdown: str) -> bool:
    combined = " ".join(
        [
            skill_draft_markdown,
            " ".join(generated_skill_draft.get("human_confirmation_points", [])),
            str(generated_skill_draft.get("review_status", "")),
        ]
    ).lower()
    return "human review" in combined or "human confirmation" in combined


def contains_prohibited_output_keys(value: Any) -> bool:
    if isinstance(value, dict):
        if PROHIBITED_OUTPUT_KEYS.intersection(value):
            return True
        return any(contains_prohibited_output_keys(child) for child in value.values())
    if isinstance(value, list):
        return any(contains_prohibited_output_keys(child) for child in value)
    return False


def build_required_human_actions(status: str, issues: list[str]) -> list[str]:
    actions = ["Review the draft before any formal Skill activation."]
    if status == "failed":
        actions.append("Fix safety review issues before using the draft as teaching material.")
    if "missing_risk_disclosure" in issues:
        actions.append("Add a risk_disclosure section to the draft.")
    if "missing_disabled_scenarios" in issues:
        actions.append("Add disabled_scenarios that fail closed for unsafe or incomplete requests.")
    return actions
