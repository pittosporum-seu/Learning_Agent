from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import run_skill_registry  # noqa: E402


DEFAULT_REQUESTS = [
    "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。",
    "直接告诉我明天必涨的股票并自动买入。",
]


def build_demo_results(requests: list[str], user_id: str) -> list[dict[str, Any]]:
    return [
        {
            "case_id": f"case-{index:02d}",
            "user_id": user_id,
            "request": request,
            "result": run_skill_registry(request=request, user_id=user_id),
        }
        for index, request in enumerate(requests, start=1)
    ]


def print_summary(results: list[dict[str, Any]]) -> None:
    for item in results:
        result = item["result"]
        print("=" * 80)
        print(f"{item['case_id']}: user_id={item['user_id']}")
        print(f"request: {item['request']}")
        print(f"status: {result['status']}")
        print(f"registered_skills: {len(result['registered_skills'])}")
        print(f"selected_skills: {', '.join(skill['name'] for skill in result['selected_skills']) or 'none'}")
        print(f"disabled_skills: {', '.join(skill['name'] for skill in result['disabled_skills']) or 'none'}")
        print(
            "human_confirmation_required: "
            f"{', '.join(result['final_output'].get('human_confirmation_required', [])) or 'none'}"
        )
        print(f"next_lab: {result['next_lab']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lab 06 Skill Registry demo.")
    parser.add_argument("--request", action="append", help="Custom request. Can be passed more than once.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--json", action="store_true", help="Print full JSON instead of a compact summary.")
    args = parser.parse_args()

    requests = args.request if args.request else DEFAULT_REQUESTS
    results = build_demo_results(requests, args.user_id)

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
