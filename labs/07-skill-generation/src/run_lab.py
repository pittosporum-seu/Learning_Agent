from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from skill_draft_builder import build_skill_draft
from skill_safety_review import PROHIBITED_OUTPUT_KEYS, review_skill_draft


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB06_RUN_LAB = REPO_ROOT / "labs" / "06-skill-registry" / "src" / "run_lab.py"


def load_lab06_module() -> Any:
    lab06_src = LAB06_RUN_LAB.parent
    if str(lab06_src) not in sys.path:
        sys.path.insert(0, str(lab06_src))
    spec = importlib.util.spec_from_file_location("lab06_skill_registry_run_lab", LAB06_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 06 runner from {LAB06_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB06 = load_lab06_module()
DEFAULT_REQUEST = _LAB06.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB06.RISK_DISCLOSURE
run_skill_registry = _LAB06.run_skill_registry


def run_skill_generation(request: str = DEFAULT_REQUEST, user_id: str = "conservative_user") -> dict[str, Any]:
    skill_registry_output = run_skill_registry(request=request, user_id=user_id)
    output: dict[str, Any] = {
        "request": request,
        "user_id": user_id,
        "status": "completed" if skill_registry_output.get("status") == "completed" else "blocked",
        "skill_registry_output": skill_registry_output,
        "generated_skill_draft": {},
        "skill_draft_markdown": "",
        "draft_review": {},
        "final_output": {},
        "risk_disclosure": skill_registry_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 08 MX Skills Adapter",
    }

    if output["status"] != "completed":
        output["draft_review"] = {
            "status": "failed",
            "issues": ["upstream_blocked"],
            "required_human_actions": [
                "Resolve the upstream blocked request before generating a Skill draft.",
                "Do not enable any Skill from a blocked flow.",
            ],
        }
        output["final_output"] = build_final_output(output)
        assert_no_prohibited_output_keys(output)
        return output

    draft_payload = build_skill_draft(skill_registry_output)
    output["generated_skill_draft"] = draft_payload["generated_skill_draft"]
    output["skill_draft_markdown"] = draft_payload["skill_draft_markdown"]
    output["draft_review"] = review_skill_draft(output["generated_skill_draft"], output["skill_draft_markdown"])
    output["final_output"] = build_final_output(output)
    assert_no_prohibited_output_keys(output)
    return output


def build_final_output(output: dict[str, Any]) -> dict[str, Any]:
    draft = output.get("generated_skill_draft") or {}
    review = output.get("draft_review") or {}
    return {
        "summary": (
            "Skill Generation completed with a reviewable draft only."
            if output["status"] == "completed"
            else "Skill Generation stopped because the upstream flow is blocked."
        ),
        "draft_name": draft.get("name"),
        "draft_only": bool(draft.get("draft")),
        "review_status": review.get("status"),
        "auto_enabled": False,
        "writes_runtime_config": False,
        "next_lab": output["next_lab"],
        "risk_disclosure": output["risk_disclosure"],
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
    parser = argparse.ArgumentParser(description="Run Lab 07 Skill Generation.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument("--input-file", help="Read request text from a UTF-8 file.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    if args.input_file:
        request = Path(args.input_file).read_text(encoding="utf-8")
    elif args.request:
        request = " ".join(args.request)
    else:
        request = DEFAULT_REQUEST

    print(json.dumps(run_skill_generation(request=request, user_id=args.user_id), ensure_ascii=False, indent=args.indent))


if __name__ == "__main__":
    main()
