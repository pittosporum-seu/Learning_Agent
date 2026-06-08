from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from strategy_intake import DEFAULT_REQUEST, parse_strategy_request  # noqa: E402


DEFAULT_REQUESTS_FILE = Path(__file__).with_name("requests.txt")


def load_requests(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Request file not found: {path}")

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
        spec = parse_strategy_request(request).to_dict()
        results.append(
            {
                "case_id": f"case-{index:02d}",
                "request": request,
                "strategy_spec": spec,
            }
        )
    return results


def print_summary(results: list[dict[str, Any]]) -> None:
    for item in results:
        spec = item["strategy_spec"]
        routing = spec["routing_decision"]
        print("=" * 80)
        print(f"{item['case_id']}: {item['request']}")
        print(f"execution_mode: {spec['execution_mode']}")
        print(f"routing_decision: {routing['mode']}")
        print(f"routing_reason: {routing['reason']}")
        print(f"matched_signals: {', '.join(routing['matched_signals']) if routing['matched_signals'] else '未命中'}")
        print(f"next_step: {routing['next_step']}")
        print(f"market: {spec['market']}")
        print(f"themes: {', '.join(spec['themes']) if spec['themes'] else '未确认'}")
        print(f"horizon_days: {spec['horizon_days'] if spec['horizon_days'] is not None else '未确认'}")
        print(f"candidate_rules: {', '.join(spec['candidate_rules']) if spec['candidate_rules'] else '未确认'}")
        print(f"risk_filters: {', '.join(spec['risk_filters']) if spec['risk_filters'] else '未确认'}")
        if spec["clarification_questions"]:
            print("clarification_questions:")
            for question in spec["clarification_questions"]:
                print(f"- {question}")
        if spec["prohibited_actions"]:
            print(f"prohibited_actions: {', '.join(spec['prohibited_actions'])}")
        print(spec["risk_disclosure"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lab 01 Strategy Intake demo.")
    parser.add_argument(
        "--request",
        action="append",
        help="Custom request. Can be passed more than once.",
    )
    parser.add_argument(
        "--requests-file",
        default=str(DEFAULT_REQUESTS_FILE),
        help="UTF-8 text file with one request per line.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON instead of a compact summary.",
    )
    args = parser.parse_args()

    if args.request:
        requests = args.request
    elif args.requests_file:
        requests = load_requests(Path(args.requests_file))
    else:
        requests = [DEFAULT_REQUEST]

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
