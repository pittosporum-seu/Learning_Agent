from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from memory_store import build_memory_snapshot
from preference_policy import apply_preferences, build_effective_user_profile, build_preference_application


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB04_RUN_LAB = REPO_ROOT / "labs" / "04-research-rag-basic" / "src" / "run_lab.py"

PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def load_lab04_module() -> Any:
    lab04_src = LAB04_RUN_LAB.parent
    if str(lab04_src) not in sys.path:
        sys.path.insert(0, str(lab04_src))
    spec = importlib.util.spec_from_file_location("lab04_research_rag_basic_run_lab", LAB04_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 04 runner from {LAB04_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB04 = load_lab04_module()
DEFAULT_REQUEST = _LAB04.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB04.RISK_DISCLOSURE
run_research_rag_basic = _LAB04.run_research_rag_basic


def run_user_preference_memory(
    request: str = DEFAULT_REQUEST,
    user_id: str = "conservative_user",
    top_k: int = 5,
) -> dict[str, Any]:
    memory_snapshot = build_memory_snapshot(user_id)
    effective_user_profile = build_effective_user_profile(memory_snapshot)
    preference_application = build_preference_application(memory_snapshot)
    memory_trace = [
        {
            "step": "load_memory_snapshot",
            "status": "completed",
            "user_id": user_id,
            "event_count": memory_snapshot["event_count"],
        },
        {
            "step": "build_effective_user_profile",
            "status": "completed",
            "applied_count": len(preference_application["applied"]),
            "ignored_count": len(preference_application["ignored"]),
        },
    ]

    rag_output = run_research_rag_basic(
        request=request,
        top_k=top_k,
        user_profile=build_strategy_user_profile(effective_user_profile),
    )
    output: dict[str, Any] = {
        "request": request,
        "user_id": user_id,
        "status": rag_output["status"],
        "memory_snapshot": memory_snapshot,
        "memory_trace": memory_trace,
        "effective_user_profile": effective_user_profile,
        "rag_output": rag_output,
        "preference_application": preference_application,
        "preference_adjusted_evidence": [],
        "final_output": {},
        "risk_disclosure": rag_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 06 Skill Registry",
    }

    if rag_output["status"] != "completed":
        output["status"] = "blocked"
        output["memory_trace"].append(
            {
                "step": "skip_preference_adjustment",
                "status": "blocked",
                "reason": "Upstream RAG output was blocked, so Memory does not continue execution.",
            }
        )
        output["final_output"] = {
            "summary": "User Preference Memory stopped because upstream Strategy Intake, Tool Use, or RAG was blocked.",
            "upstream_status": rag_output["status"],
            "adjusted_candidate_count": 0,
            "next_lab": output["next_lab"],
            "risk_disclosure": output["risk_disclosure"],
        }
        assert_no_prohibited_output_keys(output)
        return output

    preference_result = apply_preferences(rag_output["candidate_evidence"], effective_user_profile)
    output["preference_adjusted_evidence"] = preference_result["preference_adjusted_evidence"]
    output["preference_application"]["applied"].extend(preference_result["applied"])
    output["memory_trace"].append(
        {
            "step": "apply_preferences_to_evidence_view",
            "status": "completed",
            "original_candidate_count": len(rag_output["candidate_evidence"]),
            "adjusted_candidate_count": len(output["preference_adjusted_evidence"]),
        }
    )
    output["status"] = "completed"
    output["final_output"] = build_final_output(output)
    assert_no_prohibited_output_keys(output)
    return output


def build_final_output(output: dict[str, Any]) -> dict[str, Any]:
    adjusted = output["preference_adjusted_evidence"]
    return {
        "summary": "User Preference Memory completed. Preferences adjusted the evidence view without mutating original evidence.",
        "original_candidate_count": len(output["rag_output"].get("candidate_evidence", [])),
        "adjusted_candidate_count": len(adjusted),
        "report_style": output["effective_user_profile"].get("report_style"),
        "adjusted_candidate_ids": [item.get("candidate_id") for item in adjusted],
        "safety_notes": output["preference_application"].get("safety_notes", []),
        "next_lab": output["next_lab"],
        "risk_disclosure": output["risk_disclosure"],
    }


def build_strategy_user_profile(effective_user_profile: dict[str, Any]) -> dict[str, Any]:
    return {
        key: effective_user_profile[key]
        for key in ["risk_level", "exclude_st", "preferred_markets"]
        if key in effective_user_profile
    }


def assert_no_prohibited_output_keys(value: Any) -> None:
    if isinstance(value, dict):
        overlap = PROHIBITED_OUTPUT_KEYS.intersection(value)
        if overlap:
            raise AssertionError(f"Prohibited output keys found: {sorted(overlap)}")
        for child in value.values():
            assert_no_prohibited_output_keys(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_prohibited_output_keys(child)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Lab 05 User Preference Memory.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of RAG context chunks to retrieve.")
    parser.add_argument("--input-file", help="Read request text from a UTF-8 file.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    if args.input_file:
        request = Path(args.input_file).read_text(encoding="utf-8")
    elif args.request:
        request = " ".join(args.request)
    else:
        request = DEFAULT_REQUEST

    print(
        json.dumps(
            run_user_preference_memory(request=request, user_id=args.user_id, top_k=args.top_k),
            ensure_ascii=False,
            indent=args.indent,
        )
    )


if __name__ == "__main__":
    main()
