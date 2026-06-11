from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from report_builder import build_report_from_planner
from report_model import PROHIBITED_OUTPUT_KEYS, contains_prohibited_output_key, sanitize_text
from report_safety import review_report_output


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB09_RUN_LAB = REPO_ROOT / "labs" / "09-research-planner" / "src" / "run_lab.py"
NEXT_LAB = "Lab 11 Simulation Portfolio"


def load_lab09_module() -> Any:
    lab09_src = LAB09_RUN_LAB.parent
    if str(lab09_src) not in sys.path:
        sys.path.insert(0, str(lab09_src))
    spec = importlib.util.spec_from_file_location("lab09_research_planner_run_lab", LAB09_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 09 runner from {LAB09_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB09 = load_lab09_module()
DEFAULT_REQUEST = _LAB09.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB09.RISK_DISCLOSURE
run_research_planner_dag = _LAB09.run_research_planner_dag


def run_evidence_report(
    request: str = DEFAULT_REQUEST,
    user_id: str = "conservative_user",
    adapter_mode: str = "mock-finance",
    allow_real_provider: bool = False,
    capabilities: list[str] | None = None,
    env: Mapping[str, str] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    planner_output = run_research_planner_dag(
        request=request,
        user_id=user_id,
        adapter_mode=adapter_mode,
        allow_real_provider=allow_real_provider,
        capabilities=capabilities,
        env=env if env is not None else os.environ,
    )
    report_output = build_report_from_planner(planner_output, generated_at=generated_at)
    planner_summary = summarize_planner_output(planner_output)
    output: dict[str, Any] = {
        "request_summary": sanitize_text(request),
        "user_id": user_id,
        "status": report_output["status"],
        "planner_output": planner_summary,
        "evidence_report": report_output["evidence_report"],
        "report_generation_trace": report_output["report_generation_trace"],
        "evidence_refs": report_output["evidence_refs"],
        "risk_disclosure": report_output.get("risk_disclosure", RISK_DISCLOSURE),
        "human_review_required": True,
        "final_output": report_output["final_output"],
        "next_lab": report_output.get("next_lab", NEXT_LAB),
    }
    safety_review = review_report_output(output)
    output["report_safety_review"] = safety_review
    if safety_review["status"] == "failed":
        output["status"] = "failed"
    assert_no_prohibited_output_keys(output)
    return output


def summarize_planner_output(planner_output: dict[str, Any]) -> dict[str, Any]:
    adapter_output = planner_output.get("adapter_output", {})
    return {
        "status": planner_output.get("status"),
        "adapter_status": adapter_output.get("status"),
        "adapter_mode": adapter_output.get("adapter_mode"),
        "provider_mode": adapter_output.get("provider_mode"),
        "planner_trace_count": len(planner_output.get("planner_trace", [])),
        "completed_nodes": [
            node.get("node_id")
            for node in planner_output.get("research_dag", [])
            if node.get("status") == "completed"
        ],
        "blocked_nodes": [
            {
                "node_id": node.get("node_id"),
                "reason": sanitize_text(node.get("blocked_reason") or node.get("reason", "")),
            }
            for node in planner_output.get("blocked_nodes", [])
        ],
        "skipped_nodes": [
            {
                "node_id": node.get("node_id"),
                "reason": sanitize_text(node.get("skipped_reason", "")),
            }
            for node in planner_output.get("skipped_nodes", [])
        ],
        "waiting_human_confirmation_nodes": [
            {
                "node_id": node.get("node_id"),
                "required_confirmations": node.get("produced_outputs", {}).get("required_confirmations", []),
            }
            for node in planner_output.get("waiting_human_confirmation_nodes", [])
        ],
        "risk_disclosure_present": bool(planner_output.get("risk_disclosure")),
        "next_lab": planner_output.get("next_lab"),
    }


def assert_no_prohibited_output_keys(value: Any) -> None:
    if contains_prohibited_output_key(value):
        raise AssertionError(f"Prohibited output keys found: {sorted(PROHIBITED_OUTPUT_KEYS)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Lab 10 Evidence Report.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument("--adapter-mode", default="mock-finance", help="Adapter mode passed to Lab 09.")
    parser.add_argument("--allow-real-provider", action="store_true", help="Pass explicit real provider permission to Lab 09.")
    parser.add_argument("--capabilities", default="candidate-screen,market-data,finance-news", help="Comma-separated adapter capabilities.")
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
            run_evidence_report(
                request=request,
                user_id=args.user_id,
                adapter_mode=args.adapter_mode,
                allow_real_provider=args.allow_real_provider,
                capabilities=[item.strip() for item in args.capabilities.split(",") if item.strip()],
            ),
            ensure_ascii=False,
            indent=args.indent,
        )
    )


if __name__ == "__main__":
    main()
