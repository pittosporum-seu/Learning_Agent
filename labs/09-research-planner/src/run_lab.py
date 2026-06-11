from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from planner_builder import build_research_dag
from planner_executor import PROHIBITED_OUTPUT_KEYS, contains_prohibited_output_key, execute_research_planner


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB08_RUN_LAB = REPO_ROOT / "labs" / "08-mx-skills-adapter" / "src" / "run_lab.py"


def load_lab08_module() -> Any:
    lab08_src = LAB08_RUN_LAB.parent
    if str(lab08_src) not in sys.path:
        sys.path.insert(0, str(lab08_src))
    spec = importlib.util.spec_from_file_location("lab08_finance_provider_adapter_run_lab", LAB08_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 08 runner from {LAB08_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB08 = load_lab08_module()
DEFAULT_REQUEST = _LAB08.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB08.RISK_DISCLOSURE
run_finance_provider_adapter = _LAB08.run_finance_provider_adapter


def run_research_planner_dag(
    request: str = DEFAULT_REQUEST,
    user_id: str = "conservative_user",
    adapter_mode: str = "mock-finance",
    allow_real_provider: bool = False,
    capabilities: list[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    adapter_output = run_finance_provider_adapter(
        request=request,
        user_id=user_id,
        adapter_mode=adapter_mode,
        allow_real_provider=allow_real_provider,
        capabilities=capabilities,
        env=env if env is not None else os.environ,
    )
    research_dag = build_research_dag(adapter_output)
    planner_result = execute_research_planner(research_dag, adapter_output)
    output: dict[str, Any] = {
        "request": request,
        "user_id": user_id,
        "status": planner_result["status"],
        "adapter_output": adapter_output,
        "research_dag": planner_result["research_dag"],
        "planner_trace": planner_result["planner_trace"],
        "blocked_nodes": planner_result["blocked_nodes"],
        "skipped_nodes": planner_result["skipped_nodes"],
        "waiting_human_confirmation_nodes": planner_result["waiting_human_confirmation_nodes"],
        "final_output": planner_result["final_output"],
        "risk_disclosure": adapter_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 10 Evidence Report",
    }
    assert_no_prohibited_output_keys(output)
    return output


def assert_no_prohibited_output_keys(value: Any) -> None:
    if contains_prohibited_output_key(value):
        raise AssertionError(f"Prohibited output keys found: {sorted(PROHIBITED_OUTPUT_KEYS)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Lab 09 Research Planner DAG.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument("--adapter-mode", default="mock-finance", help="Adapter mode passed to Lab 08.")
    parser.add_argument("--allow-real-provider", action="store_true", help="Pass explicit real provider permission to Lab 08.")
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
            run_research_planner_dag(
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
