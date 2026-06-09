from __future__ import annotations

from copy import deepcopy
from typing import Any


SUPPORTED_FIELDS = {
    "risk_level",
    "exclude_st",
    "max_candidates",
    "preferred_markets",
    "excluded_themes",
    "excluded_risk_flags",
    "report_style",
}

DANGEROUS_FIELDS = {
    "risk_disclosure",
    "delete_sources",
    "skip_guardrails",
    "auto_trade",
    "override_evidence",
    "real_trade",
}


def build_effective_user_profile(memory_snapshot: dict[str, Any]) -> dict[str, Any]:
    effective, _ = resolve_memory_preferences(memory_snapshot)
    return effective


def build_preference_application(memory_snapshot: dict[str, Any]) -> dict[str, Any]:
    _, seed = resolve_memory_preferences(memory_snapshot)
    return {
        "applied": seed["applied"],
        "ignored": seed["ignored"],
        "safety_notes": seed["safety_notes"],
    }


def resolve_memory_preferences(memory_snapshot: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    effective = {
        key: deepcopy(value)
        for key, value in memory_snapshot.get("base_profile", {}).items()
        if key in SUPPORTED_FIELDS
    }
    applied: list[dict[str, Any]] = [
        {
            "source": "base_profile",
            "field": key,
            "value": deepcopy(value),
            "reason": "Loaded supported mock user preference.",
        }
        for key, value in effective.items()
    ]
    ignored: list[dict[str, Any]] = []
    safety_notes: list[str] = [
        "Memory can adjust the evidence view, but it cannot override evidence, sources, risk disclosure, or guardrails."
    ]

    for event in memory_snapshot.get("events", []):
        preferences = event.get("preferences") or {}
        for key, value in preferences.items():
            if key in SUPPORTED_FIELDS:
                effective[key] = deepcopy(value)
                applied.append(
                    {
                        "source": event.get("event_id"),
                        "field": key,
                        "value": deepcopy(value),
                        "reason": "Applied supported memory event preference.",
                    }
                )
            else:
                ignored.append(
                    {
                        "source": event.get("event_id"),
                        "field": key,
                        "value": summarize_ignored_value(value),
                        "reason": "Preference is unsupported or unsafe for this Lab.",
                    }
                )
                if key in DANGEROUS_FIELDS:
                    safety_notes.append(f"Ignored unsafe memory field: {key}.")

    normalize_effective_profile(effective)
    return effective, {"applied": applied, "ignored": ignored, "safety_notes": dedupe(safety_notes)}


def normalize_effective_profile(profile: dict[str, Any]) -> None:
    profile["max_candidates"] = max(0, int(profile.get("max_candidates", 10)))
    for key in ["preferred_markets", "excluded_themes", "excluded_risk_flags"]:
        value = profile.get(key)
        if value is None:
            profile[key] = []
        elif isinstance(value, list):
            profile[key] = list(value)
        else:
            profile[key] = [value]


def apply_preferences(
    candidate_evidence: list[dict[str, Any]],
    effective_user_profile: dict[str, Any],
) -> dict[str, Any]:
    adjusted = deepcopy(candidate_evidence)
    applied: list[dict[str, Any]] = []

    excluded_themes = set(effective_user_profile.get("excluded_themes", []))
    excluded_risk_flags = set(effective_user_profile.get("excluded_risk_flags", []))
    max_candidates = int(effective_user_profile.get("max_candidates", len(adjusted)))

    if excluded_themes:
        kept: list[dict[str, Any]] = []
        removed: list[str] = []
        for item in adjusted:
            if item.get("theme") in excluded_themes:
                removed.append(item.get("candidate_id", "unknown"))
            else:
                kept.append(item)
        adjusted = kept
        applied.append(
            {
                "field": "excluded_themes",
                "value": sorted(excluded_themes),
                "filtered_candidate_ids": removed,
            }
        )

    if excluded_risk_flags:
        kept = []
        removed = []
        for item in adjusted:
            risk_flags = set(item.get("risk_flags", []))
            matched_flags = sorted(risk_flags.intersection(excluded_risk_flags))
            if matched_flags:
                removed.append({"candidate_id": item.get("candidate_id"), "matched_flags": matched_flags})
            else:
                kept.append(item)
        adjusted = kept
        applied.append(
            {
                "field": "excluded_risk_flags",
                "value": sorted(excluded_risk_flags),
                "filtered_candidates": removed,
            }
        )

    before_truncate = len(adjusted)
    adjusted = adjusted[:max_candidates]
    applied.append(
        {
            "field": "max_candidates",
            "value": max_candidates,
            "truncated_count": max(0, before_truncate - len(adjusted)),
        }
    )

    return {
        "preference_adjusted_evidence": adjusted,
        "applied": applied,
    }


def summarize_ignored_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return "redacted_mock_value"
    return str(value)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
