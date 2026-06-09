from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import run_research_rag_basic  # noqa: E402


DEFAULT_REQUESTS = [
    "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。",
    "帮我找一些适合观察的股票。",
    "直接告诉我明天必涨的股票并自动买入。",
]


def build_demo_results(requests: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": f"case-{index:02d}",
            "request": request,
            "result": run_research_rag_basic(request),
        }
        for index, request in enumerate(requests, start=1)
    ]


def print_summary(results: list[dict[str, Any]]) -> None:
    for item in results:
        result = item["result"]
        print("=" * 80)
        print(f"{item['case_id']}: {item['request']}")
        print(f"status: {result['status']}")
        print(f"candidate_evidence_count: {len(result['candidate_evidence'])}")
        print(f"retrieved_context_count: {len(result['retrieved_context'])}")
        print("retrieved_context:")
        if result["retrieved_context"]:
            for context in result["retrieved_context"]:
                print(
                    f"- {context['source']}#{context['chunk_id']} | "
                    f"used_for={context['used_for']} | "
                    f"score={context['score']} | "
                    f"matched={', '.join(context['matched_terms'])}"
                )
        else:
            print("- no normal retrieval")
        print(f"next_lab: {result['next_lab']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lab 04 Research RAG Basic demo.")
    parser.add_argument("--request", action="append", help="Custom request. Can be passed more than once.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--json", action="store_true", help="Print full JSON instead of a compact summary.")
    args = parser.parse_args()

    requests = args.request if args.request else DEFAULT_REQUESTS
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
