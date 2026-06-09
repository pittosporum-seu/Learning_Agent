from __future__ import annotations

from typing import Any

from skill_registry import SkillDefinition, SkillRegistry


EXECUTION_SKILL_TYPES = {"handoff", "execution_plan"}


def build_selection_context(memory_output: dict[str, Any]) -> dict[str, Any]:
    rag_output = memory_output.get("rag_output") or {}
    strategy_spec = rag_output.get("strategy_spec") or {}
    candidate_evidence = rag_output.get("candidate_evidence") or []
    preference_adjusted_evidence = memory_output.get("preference_adjusted_evidence") or []
    retrieved_context = rag_output.get("retrieved_context") or []
    risk_disclosure = memory_output.get("risk_disclosure") or rag_output.get("risk_disclosure")
    risk_flags = sorted(
        {
            flag
            for item in candidate_evidence + preference_adjusted_evidence
            for flag in item.get("risk_flags", [])
        }
    )
    tokens = set()
    add_tokens(tokens, strategy_spec.get("output"))
    add_tokens(tokens, strategy_spec.get("execution_mode"))
    add_tokens(tokens, "risk_disclosure" if risk_disclosure else None)
    add_tokens(tokens, "candidate_evidence" if candidate_evidence else None)
    add_tokens(tokens, "preference_adjusted_evidence" if preference_adjusted_evidence else None)
    add_tokens(tokens, "retrieved_context" if retrieved_context else None)
    for flag in risk_flags:
        add_tokens(tokens, flag)
    for item in retrieved_context:
        add_tokens(tokens, item.get("used_for"))
        for term in item.get("matched_terms", []):
            add_tokens(tokens, term)
    if candidate_evidence or preference_adjusted_evidence:
        add_tokens(tokens, "observation_pool")
        add_tokens(tokens, "watchlist")
    return {
        "status": memory_output.get("status"),
        "strategy_spec": strategy_spec,
        "candidate_evidence_count": len(candidate_evidence),
        "preference_adjusted_evidence_count": len(preference_adjusted_evidence),
        "retrieved_context_count": len(retrieved_context),
        "risk_disclosure_present": bool(risk_disclosure),
        "risk_flags": risk_flags,
        "tokens": sorted(tokens),
    }


def select_skills(memory_output: dict[str, Any], registry: SkillRegistry) -> dict[str, Any]:
    context = build_selection_context(memory_output)
    selected_skills: list[dict[str, Any]] = []
    disabled_skills: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []

    for skill in registry.iter_skills():
        matched_triggers = [trigger for trigger in skill.triggers if trigger in context["tokens"]]
        disabled_reasons = build_disabled_reasons(skill, context)
        event = {
            "skill_name": skill.name,
            "skill_type": skill.skill_type,
            "matched_triggers": matched_triggers,
            "disabled_reasons": disabled_reasons,
            "requires_human_confirmation": skill.requires_human_confirmation,
        }
        trace.append(event)
        payload = {
            "name": skill.name,
            "description": skill.description,
            "skill_type": skill.skill_type,
            "matched_triggers": matched_triggers,
            "inputs": skill.inputs,
            "outputs": skill.outputs,
            "requires_human_confirmation": skill.requires_human_confirmation,
        }
        if disabled_reasons:
            disabled_skills.append({**payload, "disabled_reasons": disabled_reasons})
        elif matched_triggers:
            selected_skills.append(payload)
        else:
            disabled_skills.append({**payload, "disabled_reasons": ["no_trigger_matched"]})

    return {
        "selection_context": context,
        "skill_selection_trace": trace,
        "selected_skills": selected_skills,
        "disabled_skills": disabled_skills,
    }


def build_disabled_reasons(skill: SkillDefinition, context: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if context["status"] != "completed" and skill.skill_type in EXECUTION_SKILL_TYPES:
        reasons.append("upstream_blocked")
    if not context["risk_disclosure_present"] and skill.name in {"watchlist-handoff", "simulation-portfolio-plan"}:
        reasons.append("missing_risk_disclosure")
    if context["candidate_evidence_count"] == 0 and "candidate_evidence" in skill.inputs:
        reasons.append("missing_candidate_evidence")
    if context["preference_adjusted_evidence_count"] == 0 and "preference_adjusted_evidence" in skill.inputs:
        reasons.append("missing_preference_adjusted_evidence")
    if skill.requires_human_confirmation:
        reasons.append("requires_human_confirmation")
    return dedupe(reasons)


def add_tokens(tokens: set[str], value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str):
        tokens.add(value)
        for part in value.replace("/", " ").replace(",", " ").replace(";", " ").split():
            tokens.add(part)
    elif isinstance(value, list):
        for item in value:
            add_tokens(tokens, item)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
