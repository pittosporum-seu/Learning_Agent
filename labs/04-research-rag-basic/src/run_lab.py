from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from rag_context import build_rag_context


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB03_RUN_LAB = REPO_ROOT / "labs" / "03-finance-tool-use-mock" / "src" / "run_lab.py"

PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def load_lab03_module() -> Any:
    lab03_src = LAB03_RUN_LAB.parent
    if str(lab03_src) not in sys.path:
        sys.path.insert(0, str(lab03_src))
    spec = importlib.util.spec_from_file_location("lab03_finance_tool_use_run_lab", LAB03_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 03 runner from {LAB03_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB03 = load_lab03_module()
DEFAULT_REQUEST = _LAB03.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB03.RISK_DISCLOSURE
run_finance_tool_use_mock = _LAB03.run_finance_tool_use_mock


def run_research_rag_basic(
    request: str = DEFAULT_REQUEST,
    top_k: int = 5,
    user_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lab03_output = run_finance_tool_use_mock(request, user_profile=user_profile)
    output: dict[str, Any] = {
        "request": request,
        "status": lab03_output["status"],
        "strategy_spec": lab03_output["strategy_spec"],
        "tool_trace": lab03_output["tool_trace"],
        "candidate_evidence": lab03_output["candidate_evidence"],
        "retrieval_trace": [],
        "retrieved_context": [],
        "augmented_evidence": [],
        "final_output": {},
        "risk_disclosure": lab03_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 05 User Preference Memory",
    }

    if lab03_output["status"] != "completed":
        output["status"] = "blocked"
        output["retrieval_trace"] = [
            {
                "step": "skip_retrieval",
                "status": "blocked",
                "reason": "Lab 03 stopped before candidate evidence, so Lab 04 does not run normal retrieval.",
                "upstream_status": lab03_output["status"],
            }
        ]
        output["final_output"] = {
            "summary": "Research RAG Basic stopped because upstream Strategy Intake or Tool Use was blocked.",
            "upstream_summary": lab03_output.get("final_output", {}).get("summary"),
            "retrieved_context_count": 0,
            "next_lab": output["next_lab"],
            "risk_disclosure": output["risk_disclosure"],
        }
        assert_no_prohibited_output_keys(output)
        return output

    rag_output = build_rag_context(
        strategy_spec=output["strategy_spec"],
        candidate_evidence=output["candidate_evidence"],
        top_k=top_k,
    )
    output["status"] = "completed"
    output["retrieval_trace"] = rag_output["retrieval_trace"]
    output["retrieved_context"] = rag_output["retrieved_context"]
    output["augmented_evidence"] = rag_output["augmented_evidence"]
    output["final_output"] = build_final_output(output)
    assert_no_prohibited_output_keys(output)
    return output


def build_final_output(output: dict[str, Any]) -> dict[str, Any]:
    retrieved_context = output["retrieved_context"]
    used_for = sorted({item["used_for"] for item in retrieved_context})
    sources = sorted({f"{item['source']}#{item['chunk_id']}" for item in retrieved_context})
    return {
        "summary": "Research RAG Basic completed. Local mock documents were retrieved and attached to candidate evidence.",
        "candidate_count": len(output["candidate_evidence"]),
        "retrieved_context_count": len(retrieved_context),
        "used_for": used_for,
        "sources": sources,
        "evidence_gap_notes": [
            "Retrieved context comes from local mock markdown files only.",
            "No real model, vector database, finance API, or news API was called.",
            "The output is an evidence assembly demo, not investment advice.",
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
    parser = argparse.ArgumentParser(description="Run Lab 04 Research RAG Basic.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--input-file", help="Read request text from a UTF-8 file.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of context chunks to retrieve.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    if args.input_file:
        request = Path(args.input_file).read_text(encoding="utf-8")
    elif args.request:
        request = " ".join(args.request)
    else:
        request = DEFAULT_REQUEST

    print(json.dumps(run_research_rag_basic(request, top_k=args.top_k), ensure_ascii=False, indent=args.indent))


if __name__ == "__main__":
    main()
