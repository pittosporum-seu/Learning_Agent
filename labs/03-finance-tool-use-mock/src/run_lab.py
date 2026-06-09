from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB01_SRC = REPO_ROOT / "labs" / "01-strategy-intake" / "src"
sys.path.insert(0, str(LAB01_SRC))

from strategy_intake import DEFAULT_REQUEST, RISK_DISCLOSURE, parse_strategy_request  # noqa: E402
from evidence import build_candidate_evidence  # noqa: E402
from tool_registry import ToolRegistry, build_default_registry  # noqa: E402


BLOCKED_ROUTING_MODES = {"blocked", "needs_clarification"}
PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def run_finance_tool_use_mock(
    request: str = DEFAULT_REQUEST,
    registry: ToolRegistry | None = None,
    user_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or build_default_registry()
    strategy_spec = parse_strategy_request(request, user_profile=user_profile).to_dict()
    routing_mode = (strategy_spec.get("routing_decision") or {}).get("mode")

    output: dict[str, Any] = {
        "request": request,
        "status": "running",
        "strategy_spec": strategy_spec,
        "registered_tools": registry.list_tools(),
        "tool_trace": [],
        "candidate_evidence": [],
        "final_output": {},
        "next_lab": "Lab 04 Research RAG Basic",
        "risk_disclosure": strategy_spec.get("risk_disclosure", RISK_DISCLOSURE),
    }

    if routing_mode in BLOCKED_ROUTING_MODES:
        output["status"] = "blocked"
        output["final_output"] = {
            "summary": "Strategy request stopped before tool use because routing requires clarification or blocking.",
            "routing_mode": routing_mode,
            "clarification_questions": strategy_spec.get("clarification_questions", []),
            "prohibited_actions": strategy_spec.get("prohibited_actions", []),
            "safe_next_step": "Revise the request before any mock finance tool is selected.",
            "risk_disclosure": output["risk_disclosure"],
        }
        return output

    select_result = call_tool_with_trace(
        registry=registry,
        trace=output["tool_trace"],
        tool_name="select_candidates",
        selected_reason="StrategySpec has enough theme and rule information to query the mock universe.",
        strategy_spec=strategy_spec,
    )
    candidates = select_result.get("candidates", [])
    candidate_ids = [candidate["candidate_id"] for candidate in candidates]

    market_result = call_tool_with_trace(
        registry=registry,
        trace=output["tool_trace"],
        tool_name="fetch_market_data",
        selected_reason="Candidate ids from the mock universe need trend and drawdown evidence.",
        candidate_ids=candidate_ids,
    )
    news_result = call_tool_with_trace(
        registry=registry,
        trace=output["tool_trace"],
        tool_name="search_finance_news",
        selected_reason="Candidate ids need mock news snippets and risk flags before evidence assembly.",
        candidate_ids=candidate_ids,
    )

    output["candidate_evidence"] = build_candidate_evidence(candidates, market_result, news_result)
    output["status"] = "completed"
    output["final_output"] = {
        "summary": "Mock Tool Use completed. Tool results were converted into candidate evidence, not investment advice.",
        "candidate_count": len(output["candidate_evidence"]),
        "tool_call_count": len(output["tool_trace"]),
        "evidence_item_count": sum(len(item["evidence_items"]) for item in output["candidate_evidence"]),
        "risk_flags": sorted({flag for item in output["candidate_evidence"] for flag in item.get("risk_flags", [])}),
        "next_lab": output["next_lab"],
        "risk_disclosure": output["risk_disclosure"],
    }
    assert_no_prohibited_output_keys(output)
    return output


def call_tool_with_trace(
    registry: ToolRegistry,
    trace: list[dict[str, Any]],
    tool_name: str,
    selected_reason: str,
    **kwargs: Any,
) -> dict[str, Any]:
    tool = registry.get(tool_name)
    event: dict[str, Any] = {
        "turn": len(trace) + 1,
        "tool_name": tool.name,
        "provider": tool.provider,
        "selected_reason": selected_reason,
        "input": sanitize_tool_input(kwargs),
        "status": "running",
        "output": {},
        "error": None,
    }
    try:
        result = registry.call(tool_name, **kwargs)
    except Exception as exc:  # pragma: no cover - kept for failure-path readability.
        event["status"] = "failed"
        event["error"] = str(exc)
        event["output"] = {"ok": False, "summary": f"{tool_name} failed."}
        trace.append(event)
        return event["output"]

    event["status"] = "success"
    event["output"] = summarize_tool_output(tool_name, result)
    trace.append(event)
    return result


def sanitize_tool_input(kwargs: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(kwargs)
    if "strategy_spec" in sanitized:
        spec = sanitized["strategy_spec"]
        sanitized["strategy_spec"] = {
            "market": spec.get("market"),
            "themes": spec.get("themes", []),
            "candidate_rules": spec.get("candidate_rules", []),
            "risk_filters": spec.get("risk_filters", []),
            "execution_mode": spec.get("execution_mode"),
        }
    return sanitized


def summarize_tool_output(tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "select_candidates":
        return {
            "ok": True,
            "summary": f"Selected {len(result.get('candidates', []))} mock candidates.",
            "candidate_ids": [item["candidate_id"] for item in result.get("candidates", [])],
            "rejected_count": len(result.get("rejected", [])),
        }
    if tool_name == "fetch_market_data":
        return {
            "ok": True,
            "summary": f"Fetched market evidence for {len(result.get('market_items', []))} mock candidates.",
            "candidate_ids": [item["candidate_id"] for item in result.get("market_items", [])],
            "missing_candidate_ids": result.get("missing_candidate_ids", []),
        }
    if tool_name == "search_finance_news":
        return {
            "ok": True,
            "summary": f"Fetched {len(result.get('news_items', []))} mock news snippets.",
            "risk_flags": result.get("risk_flags", []),
        }
    return {"ok": True, "summary": f"{tool_name} completed."}


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
    parser = argparse.ArgumentParser(description="Run Lab 03 Finance Tool Use Mock.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--input-file", help="Read request text from a UTF-8 file.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    if args.input_file:
        request = Path(args.input_file).read_text(encoding="utf-8")
    elif args.request:
        request = " ".join(args.request)
    else:
        request = DEFAULT_REQUEST

    print(json.dumps(run_finance_tool_use_mock(request), ensure_ascii=False, indent=args.indent))


if __name__ == "__main__":
    main()
