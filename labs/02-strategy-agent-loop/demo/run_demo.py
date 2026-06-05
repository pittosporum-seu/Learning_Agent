from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from agent_loop import run_strategy_agent_loop  # noqa: E402


DEFAULT_REQUESTS_FILE = Path(__file__).with_name("requests.txt")


def load_requests(path: Path) -> list[str]:
    requests: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        requests.append(text)
    return requests


def build_demo_results(requests: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for index, request in enumerate(requests, start=1):
        state = run_strategy_agent_loop(request).to_dict()
        results.append(
            {
                "case_id": f"case-{index:02d}",
                "request": request,
                "loop_state": state,
            }
        )
    return results


def print_summary(results: list[dict[str, Any]]) -> None:
    for item in results:
        state = item["loop_state"]
        spec = state.get("strategy_spec") or {}
        print("=" * 80)
        print(f"{item['case_id']}: {item['request']}")
        print(f"status: {state['status']}")
        print(f"execution_mode: {spec.get('execution_mode', 'n/a')}")
        print(f"themes: {', '.join(spec.get('themes') or []) or '未确认'}")
        print(f"trace: {' -> '.join(event['action'] for event in state['trace'])}")
        if state["research_plan"]:
            print("research_plan:")
            for step in state["research_plan"]:
                marker = " [human]" if step["requires_human_confirmation"] else ""
                print(f"- {step['step_id']}: {step['purpose']}{marker}")
        else:
            print("research_plan: 未生成")
        if state["final_output"].get("clarification_questions"):
            print("clarification_questions:")
            for question in state["final_output"]["clarification_questions"]:
                print(f"- {question}")
        if state["final_output"].get("prohibited_actions"):
            print(f"prohibited_actions: {', '.join(state['final_output']['prohibited_actions'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lab 02 Strategy Agent Loop demo.")
    parser.add_argument("--request", action="append", help="Custom request. Can be passed more than once.")
    parser.add_argument("--requests-file", default=str(DEFAULT_REQUESTS_FILE), help="UTF-8 text file with one request per line.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--json", action="store_true", help="Print full JSON instead of a compact summary.")
    args = parser.parse_args()

    requests = args.request if args.request else load_requests(Path(args.requests_file))
    results = build_demo_results(requests)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote demo output: {output_path}")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_summary(results)


if __name__ == "__main__":
    main()
