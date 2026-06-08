from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB01_SRC = REPO_ROOT / "labs" / "01-strategy-intake" / "src"
sys.path.insert(0, str(LAB01_SRC))

from strategy_intake import DEFAULT_REQUEST, RISK_DISCLOSURE, parse_strategy_request  # noqa: E402


@dataclass
class TraceEvent:
    turn: int
    observation: str
    decision: str
    why_this_action: str
    action: str
    result: dict[str, Any]
    guardrail_triggered: bool
    next_action_hint: str
    status: str


@dataclass
class LoopState:
    request: str
    status: str = "running"
    strategy_spec: dict[str, Any] | None = None
    research_plan: list[dict[str, Any]] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)
    final_output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["trace"] = [asdict(event) for event in self.trace]
        return data


def run_strategy_agent_loop(request: str = DEFAULT_REQUEST, max_turns: int = 8) -> LoopState:
    state = LoopState(request=request)

    for turn in range(1, max_turns + 1):
        observation = observe_state(state)
        action = decide_next_action(state)
        result = execute_action(state, action)
        state.trace.append(
            TraceEvent(
                turn=turn,
                observation=observation,
                decision=describe_decision(action),
                why_this_action=describe_why_this_action(action, observation, state),
                action=action,
                result=result,
                guardrail_triggered=guardrail_was_triggered(action, result),
                next_action_hint=build_next_action_hint(state, action, result),
                status=state.status,
            )
        )

        if state.status in {"completed", "blocked", "failed"}:
            break
    else:
        state.status = "failed"
        state.error = f"Loop exceeded max_turns={max_turns}."
        state.final_output = {
            "summary": "Agent loop stopped by max_turns guardrail.",
            "max_turns_guardrail": True,
            "risk_disclosure": RISK_DISCLOSURE,
        }
        state.trace.append(
            TraceEvent(
                turn=max_turns + 1,
                observation="Loop turn budget is exhausted before reaching a terminal state.",
                decision="Fail closed because the loop exceeded the configured max_turns.",
                why_this_action="The max_turns guardrail prevents uncontrolled or unclear loops from continuing.",
                action="max_turns_guardrail",
                result={
                    "ok": False,
                    "summary": "Stopped by max_turns guardrail.",
                    "details": {
                        "max_turns": max_turns,
                        "safe_next_step": "Inspect the trace and raise max_turns only after confirming the loop is bounded.",
                    },
                },
                guardrail_triggered=True,
                next_action_hint="Stop the loop and review the trace before retrying.",
                status=state.status,
            )
        )

    return state


def observe_state(state: LoopState) -> str:
    if state.strategy_spec is None:
        return "No StrategySpec yet."
    if state.strategy_spec.get("clarification_questions"):
        return "StrategySpec needs user clarification."
    if state.strategy_spec.get("prohibited_actions"):
        return "StrategySpec contains prohibited actions."
    if not state.research_plan:
        return "StrategySpec is ready; research plan has not been built."
    if not state.final_output:
        return "Research plan is ready; final output has not been prepared."
    return "Loop has completed."


def decide_next_action(state: LoopState) -> str:
    if state.strategy_spec is None:
        return "parse_strategy"

    if state.strategy_spec.get("clarification_questions") or state.strategy_spec.get("prohibited_actions"):
        return "request_clarification"

    if not state.research_plan:
        return "build_research_plan"

    if not state.final_output:
        return "finalize"

    return "stop"


def execute_action(state: LoopState, action: str) -> dict[str, Any]:
    if action == "parse_strategy":
        spec = parse_strategy_request(state.request).to_dict()
        state.strategy_spec = spec
        routing_decision = spec.get("routing_decision", {})
        return {
            "ok": True,
            "summary": (
                "Parsed request into StrategySpec "
                f"with execution_mode={spec['execution_mode']} and routing_mode={routing_decision.get('mode')}."
            ),
            "execution_mode": spec["execution_mode"],
            "routing_mode": routing_decision.get("mode"),
            "matched_signals": routing_decision.get("matched_signals", []),
            "details": {
                "requires_agent": spec.get("requires_agent"),
                "clarification_question_count": len(spec.get("clarification_questions", [])),
                "prohibited_action_count": len(spec.get("prohibited_actions", [])),
            },
        }

    if action == "request_clarification":
        return request_clarification(state)

    if action == "build_research_plan":
        state.research_plan = build_research_plan(state.strategy_spec or {})
        planned_tools = [
            step["mock_tool"]
            for step in state.research_plan
            if step.get("mock_tool")
        ]
        requires_human_confirmation = any(step.get("requires_human_confirmation") for step in state.research_plan)
        return {
            "ok": True,
            "summary": f"Built research plan with {len(state.research_plan)} steps.",
            "plan_step_count": len(state.research_plan),
            "planned_tools": planned_tools,
            "requires_human_confirmation": requires_human_confirmation,
            "details": {
                "step_ids": [step["step_id"] for step in state.research_plan],
            },
        }

    if action == "finalize":
        state.status = "completed"
        state.final_output = build_final_output(state)
        return {
            "ok": True,
            "summary": state.final_output["summary"],
            "next_lab": state.final_output["next_lab"],
            "details": {
                "plan_step_ids": state.final_output["plan_step_ids"],
            },
        }

    if action == "stop":
        state.status = "completed"
        return {
            "ok": True,
            "summary": "Loop already complete.",
            "details": {},
        }

    state.status = "failed"
    state.error = f"Unknown action: {action}"
    return {
        "ok": False,
        "summary": state.error,
        "details": {
            "safe_next_step": "Stop and inspect the action router.",
        },
    }


def request_clarification(state: LoopState) -> dict[str, Any]:
    spec = state.strategy_spec or {}
    safe_next_step = "Revise the request into a research or watchlist question."
    state.status = "blocked"
    state.final_output = {
        "summary": "Strategy request cannot move forward until the user clarifies or removes unsafe intent.",
        "clarification_questions": spec.get("clarification_questions", []),
        "prohibited_actions": spec.get("prohibited_actions", []),
        "next_action_for_user": safe_next_step,
        "safe_next_step": safe_next_step,
        "risk_disclosure": spec.get("risk_disclosure", RISK_DISCLOSURE),
    }
    return {
        "ok": False,
        "summary": "Blocked and prepared clarification request.",
        "clarification_questions": spec.get("clarification_questions", []),
        "prohibited_actions": spec.get("prohibited_actions", []),
        "safe_next_step": safe_next_step,
        "details": {
            "routing_mode": (spec.get("routing_decision") or {}).get("mode"),
            "matched_signals": (spec.get("routing_decision") or {}).get("matched_signals", []),
        },
    }


def build_research_plan(spec: dict[str, Any]) -> list[dict[str, Any]]:
    if spec.get("execution_mode") == "workflow":
        return build_workflow_plan(spec)
    return build_agent_plan(spec)


def build_workflow_plan(spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "validate_strategy_spec",
            "purpose": "Confirm required screening fields are present.",
            "inputs": ["strategy_spec"],
            "outputs": ["validated_strategy_spec"],
            "mock_tool": None,
            "requires_human_confirmation": False,
        },
        {
            "step_id": "run_screening_workflow",
            "purpose": "Apply deterministic screening conditions in a fixed order.",
            "inputs": ["themes", "candidate_rules", "risk_filters"],
            "outputs": ["screening_plan"],
            "mock_tool": "local_rule_filter",
            "requires_human_confirmation": False,
        },
        {
            "step_id": "produce_structured_summary",
            "purpose": "Generate a structured summary without stock recommendations.",
            "inputs": ["screening_plan"],
            "outputs": ["strategy_summary"],
            "mock_tool": None,
            "requires_human_confirmation": False,
        },
    ]


def build_agent_plan(spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "generate_candidate_pool",
            "purpose": "Translate themes and candidate rules into an initial candidate-pool query.",
            "inputs": ["market", "themes", "candidate_rules", "user_preferences"],
            "outputs": ["candidate_pool_query"],
            "mock_tool": "mx-xuangu-mock",
            "requires_human_confirmation": False,
        },
        {
            "step_id": "check_market_and_financial_data",
            "purpose": "Collect market, valuation, liquidity, and basic financial evidence.",
            "inputs": ["candidate_pool_query", "horizon_days"],
            "outputs": ["market_financial_evidence"],
            "mock_tool": "mx-data-mock",
            "requires_human_confirmation": False,
        },
        {
            "step_id": "check_news_and_risk_events",
            "purpose": "Check news, announcements, and negative-event signals.",
            "inputs": ["themes", "risk_filters", "horizon_days"],
            "outputs": ["news_risk_evidence"],
            "mock_tool": "mx-search-mock",
            "requires_human_confirmation": False,
        },
        {
            "step_id": "build_evidence_report",
            "purpose": "Assemble evidence, uncertainty, and risk disclosure into a report draft.",
            "inputs": ["market_financial_evidence", "news_risk_evidence"],
            "outputs": ["evidence_report_draft"],
            "mock_tool": None,
            "requires_human_confirmation": False,
        },
        {
            "step_id": "human_review",
            "purpose": "Ask the user to review before adding watchlist or entering simulation.",
            "inputs": ["evidence_report_draft"],
            "outputs": ["approved_next_action"],
            "mock_tool": None,
            "requires_human_confirmation": True,
        },
    ]


def build_final_output(state: LoopState) -> dict[str, Any]:
    spec = state.strategy_spec or {}
    return {
        "summary": "Strategy Agent Loop completed a mock planning pass.",
        "execution_mode": spec.get("execution_mode"),
        "market": spec.get("market"),
        "themes": spec.get("themes", []),
        "horizon_days": spec.get("horizon_days"),
        "plan_step_ids": [step["step_id"] for step in state.research_plan],
        "next_lab": "Lab 03 will replace mock_tool placeholders with callable mock finance tools.",
        "risk_disclosure": spec.get("risk_disclosure", RISK_DISCLOSURE),
    }


def describe_decision(action: str) -> str:
    return {
        "parse_strategy": "Parse the natural-language request before planning.",
        "request_clarification": "Stop and ask for clarification or safer wording.",
        "build_research_plan": "Build a research plan from the valid StrategySpec.",
        "finalize": "Prepare final output and stop the loop.",
        "stop": "No further action is needed.",
        "max_turns_guardrail": "Fail closed because max_turns was exceeded.",
    }.get(action, "Unknown action.")


def describe_why_this_action(action: str, observation: str, state: LoopState) -> str:
    if action == "parse_strategy":
        return "The loop cannot decide or plan until the natural-language request becomes a StrategySpec."
    if action == "request_clarification":
        spec = state.strategy_spec or {}
        if spec.get("prohibited_actions"):
            return "The StrategySpec contains prohibited or high-risk intent, so the loop must fail closed."
        return "Required strategy details are missing, so planning would be unsafe or ambiguous."
    if action == "build_research_plan":
        return "The StrategySpec is complete enough to produce a mock research plan without calling real tools."
    if action == "finalize":
        return "The mock research plan is ready, so the loop can prepare the handoff summary for later Labs."
    if action == "stop":
        return "The loop already reached a terminal state."
    return f"The action router selected {action} after observing: {observation}"


def guardrail_was_triggered(action: str, result: dict[str, Any]) -> bool:
    return action in {"request_clarification", "max_turns_guardrail"} or result.get("ok") is False


def build_next_action_hint(state: LoopState, action: str, result: dict[str, Any]) -> str:
    if action == "parse_strategy":
        if (state.strategy_spec or {}).get("clarification_questions") or (state.strategy_spec or {}).get("prohibited_actions"):
            return "Next loop should request clarification and stop safely."
        return "Next loop should build a mock research plan."
    if action == "build_research_plan":
        return "Next loop should finalize the planning summary."
    if action == "request_clarification":
        return result.get("safe_next_step", "Wait for a safer revised request.")
    if action == "finalize":
        return "Loop is complete; Lab 03 can consume the mock_tool placeholders later."
    if action == "max_turns_guardrail":
        return "Stop the loop and review the trace before retrying."
    if state.status == "failed":
        return "Stop and inspect the failed action."
    return "No further action is needed."


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lab 02 Strategy Agent Loop.")
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

    state = run_strategy_agent_loop(request)
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=args.indent))


if __name__ == "__main__":
    main()
