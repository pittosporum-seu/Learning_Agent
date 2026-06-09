from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from skill_registry import SkillRegistry, build_default_registry
from skill_selector import select_skills


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB05_RUN_LAB = REPO_ROOT / "labs" / "05-user-preference-memory" / "src" / "run_lab.py"

PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def load_lab05_module() -> Any:
    lab05_src = LAB05_RUN_LAB.parent
    if str(lab05_src) not in sys.path:
        sys.path.insert(0, str(lab05_src))
    spec = importlib.util.spec_from_file_location("lab05_user_preference_memory_run_lab", LAB05_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 05 runner from {LAB05_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB05 = load_lab05_module()
DEFAULT_REQUEST = _LAB05.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB05.RISK_DISCLOSURE
run_user_preference_memory = _LAB05.run_user_preference_memory


def run_skill_registry(
    request: str = DEFAULT_REQUEST,
    user_id: str = "conservative_user",
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    registry = registry or build_default_registry()
    memory_output = run_user_preference_memory(request=request, user_id=user_id)
    selection = select_skills(memory_output, registry)
    output: dict[str, Any] = {
        "request": request,
        "user_id": user_id,
        "status": "completed" if memory_output.get("status") == "completed" else "blocked",
        "memory_output": memory_output,
        "registered_skills": registry.list_skills(),
        "skill_selection_trace": selection["skill_selection_trace"],
        "selected_skills": selection["selected_skills"],
        "disabled_skills": selection["disabled_skills"],
        "final_output": {},
        "risk_disclosure": memory_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 07 Skill Generation",
    }
    output["final_output"] = build_final_output(output)
    assert_no_prohibited_output_keys(output)
    return output


def build_final_output(output: dict[str, Any]) -> dict[str, Any]:
    selected_names = [skill["name"] for skill in output["selected_skills"]]
    disabled_names = [skill["name"] for skill in output["disabled_skills"]]
    return {
        "summary": "Skill Registry completed. Mock Skills were selected or disabled from metadata and guardrails only.",
        "selected_skill_count": len(selected_names),
        "disabled_skill_count": len(disabled_names),
        "selected_skills": selected_names,
        "disabled_skills": disabled_names,
        "human_confirmation_required": [
            skill["name"]
            for skill in output["selected_skills"] + output["disabled_skills"]
            if skill.get("requires_human_confirmation")
        ],
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
    parser = argparse.ArgumentParser(description="Run Lab 06 Skill Registry.")
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

    print(
        json.dumps(
            run_skill_registry(request=request, user_id=args.user_id),
            ensure_ascii=False,
            indent=args.indent,
        )
    )


if __name__ == "__main__":
    main()
