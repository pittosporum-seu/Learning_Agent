from __future__ import annotations

from copy import deepcopy
from typing import Any

from dag_model import ResearchDagNode, get_dependency_statuses, topological_sort_nodes


PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}
ADAPTER_CAPABILITIES = ["candidate-screen", "market-data", "finance-news"]


def execute_research_planner(nodes: list[ResearchDagNode], adapter_output: dict[str, Any]) -> dict[str, Any]:
    working_nodes = [ResearchDagNode.from_dict(node.to_dict()) for node in nodes]
    planner_trace: list[dict[str, Any]] = []

    for node in topological_sort_nodes(working_nodes):
        dependency_status = get_dependency_statuses(working_nodes, node)
        blocked_dependencies = {
            dependency: status
            for dependency, status in dependency_status.items()
            if status in {"blocked", "skipped"}
        }
        if blocked_dependencies:
            set_node_state(
                node,
                status="skipped",
                produced_outputs={},
                skipped_reason=f"dependency did not complete: {blocked_dependencies}",
            )
            planner_trace.append(build_trace_event(node, dependency_status, "pending", "Skipped because dependency did not complete."))
            continue

        started_from = node.status
        execute_node(node, adapter_output)
        planner_trace.append(build_trace_event(node, dependency_status, started_from, status_reason(node)))

    if contains_prohibited_output_key(adapter_output) or contains_prohibited_output_key([node.to_dict() for node in working_nodes]):
        block_planner_for_prohibited_output(working_nodes, planner_trace)

    blocked_nodes = [node.to_dict() for node in working_nodes if node.status == "blocked"]
    skipped_nodes = [node.to_dict() for node in working_nodes if node.status == "skipped"]
    waiting_nodes = [node.to_dict() for node in working_nodes if node.status == "waiting_human_confirmation"]
    status = resolve_run_status(blocked_nodes, waiting_nodes)
    final_output = build_final_output(working_nodes, status, adapter_output)
    return {
        "status": status,
        "research_dag": [node.to_dict() for node in working_nodes],
        "planner_trace": planner_trace,
        "blocked_nodes": blocked_nodes,
        "skipped_nodes": skipped_nodes,
        "waiting_human_confirmation_nodes": waiting_nodes,
        "final_output": final_output,
    }


def execute_node(node: ResearchDagNode, adapter_output: dict[str, Any]) -> None:
    adapter_status = adapter_output.get("status")
    adapter_mode = adapter_output.get("adapter_mode", "")
    safety_gate = adapter_output.get("safety_gate", {})
    risk_disclosure = adapter_output.get("risk_disclosure", "")

    if node.node_id == "parse_and_route":
        routing_status = "ready" if adapter_status == "completed" else "blocked_upstream"
        set_node_state(
            node,
            status="completed",
            produced_outputs={
                "routing_status": routing_status,
                "strategy_spec_present": bool(extract_strategy_spec(adapter_output)),
                "adapter_status": adapter_status,
            },
        )
        return

    if node.node_id == "adapter_capability_check":
        if adapter_status != "completed":
            set_node_state(
                node,
                status="blocked",
                produced_outputs={"adapter_status": adapter_status},
                blocked_reason="Lab 08 adapter output is not completed.",
            )
            return
        if adapter_mode == "external-finance" and not safety_gate.get("real_provider_allowed"):
            set_node_state(
                node,
                status="blocked",
                produced_outputs={"adapter_mode": adapter_mode, "real_provider_allowed": False},
                blocked_reason="External finance provider did not pass safety gate.",
            )
            return
        set_node_state(
            node,
            status="completed",
            produced_outputs={
                "adapter_mode": adapter_mode,
                "provider_mode": adapter_output.get("provider_mode"),
                "available_capabilities": successful_capabilities(adapter_output),
                "real_provider_allowed": bool(safety_gate.get("real_provider_allowed")),
            },
        )
        return

    if node.node_id == "candidate_generation":
        event = find_adapter_event(adapter_output, "candidate-screen")
        if not adapter_event_successful(event):
            set_node_state(node, "blocked", {"capability": "candidate-screen"}, "candidate-screen adapter result is unavailable.")
            return
        candidates = event.get("output", {}).get("candidates", [])
        set_node_state(
            node,
            "completed",
            {
                "candidate_count": len(candidates),
                "candidate_ids": [item.get("candidate_id") for item in candidates],
                "source": event.get("adapter_name"),
            },
        )
        return

    if node.node_id == "market_data_check":
        event = find_adapter_event(adapter_output, "market-data")
        if not adapter_event_successful(event):
            set_node_state(node, "blocked", {"capability": "market-data"}, "market-data adapter result is unavailable.")
            return
        market_items = event.get("output", {}).get("market_items", [])
        set_node_state(
            node,
            "completed",
            {
                "market_evidence_count": len(market_items),
                "missing_candidate_ids": event.get("output", {}).get("missing_candidate_ids", []),
                "source": event.get("adapter_name"),
            },
        )
        return

    if node.node_id == "news_risk_check":
        event = find_adapter_event(adapter_output, "finance-news")
        if not adapter_event_successful(event):
            set_node_state(node, "blocked", {"capability": "finance-news"}, "finance-news adapter result is unavailable.")
            return
        output = event.get("output", {})
        set_node_state(
            node,
            "completed",
            {
                "news_item_count": len(output.get("news_items", [])),
                "risk_flags": output.get("risk_flags", []),
                "source": event.get("adapter_name"),
            },
        )
        return

    if node.node_id == "evidence_context_attach":
        set_node_state(
            node,
            "completed",
            {
                "adapter_trace_count": len(adapter_output.get("adapter_trace", [])),
                "evidence_gaps": [],
                "context_attached": True,
            },
        )
        return

    if node.node_id == "memory_preference_adjustment":
        memory_output = extract_memory_output(adapter_output)
        set_node_state(
            node,
            "completed",
            {
                "memory_trace_present": bool(memory_output.get("memory_trace")),
                "preference_view_present": bool(memory_output.get("preference_adjusted_evidence")),
                "original_evidence_preserved": True,
            },
        )
        return

    if node.node_id == "skill_selection":
        skill_output = extract_skill_registry_output(adapter_output)
        set_node_state(
            node,
            "completed",
            {
                "selected_skill_count": len(skill_output.get("selected_skills", [])),
                "disabled_skill_count": len(skill_output.get("disabled_skills", [])),
                "skill_selection_trace_present": bool(skill_output.get("skill_selection_trace")),
            },
        )
        return

    if node.node_id == "human_review_gate":
        if not risk_disclosure:
            set_node_state(
                node,
                "blocked",
                {"risk_disclosure_present": False},
                "missing risk_disclosure",
            )
            return
        set_node_state(
            node,
            "waiting_human_confirmation",
            {
                "risk_disclosure_present": True,
                "required_confirmations": [
                    "review evidence before publishing a report",
                    "confirm before changing any watchlist or simulation state",
                    "review before enabling generated skills",
                ],
                "blocked_until_confirmed": [
                    "external publication",
                    "watchlist handoff",
                    "simulation handoff",
                    "skill activation",
                ],
            },
        )
        return

    set_node_state(node, "blocked", {}, f"Unknown node: {node.node_id}")


def set_node_state(
    node: ResearchDagNode,
    status: str,
    produced_outputs: dict[str, Any],
    blocked_reason: str = "",
    skipped_reason: str = "",
) -> None:
    node.status = status
    node.produced_outputs = produced_outputs
    node.blocked_reason = blocked_reason if status == "blocked" else ""
    node.skipped_reason = skipped_reason if status == "skipped" else ""


def build_trace_event(
    node: ResearchDagNode,
    dependency_status: dict[str, str],
    started_from: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "status": node.status,
        "reason": reason,
        "dependency_status": dependency_status,
        "started_from": started_from,
        "produced_outputs": node.produced_outputs,
        "blocked_reason": node.blocked_reason,
        "skipped_reason": node.skipped_reason,
    }


def status_reason(node: ResearchDagNode) -> str:
    if node.status == "completed":
        return f"{node.node_id} completed from available mock planner context."
    if node.status == "waiting_human_confirmation":
        return "Human review gate reached; automatic completion is not allowed."
    if node.status == "blocked":
        return node.blocked_reason
    if node.status == "skipped":
        return node.skipped_reason
    return f"{node.node_id} ended with status {node.status}."


def find_adapter_event(adapter_output: dict[str, Any], capability: str) -> dict[str, Any]:
    for event in adapter_output.get("adapter_trace", []):
        if event.get("capability") == capability:
            return event
    return {}


def adapter_event_successful(event: dict[str, Any]) -> bool:
    return bool(event) and event.get("status") == "success"


def successful_capabilities(adapter_output: dict[str, Any]) -> list[str]:
    return [
        event.get("capability", "")
        for event in adapter_output.get("adapter_trace", [])
        if event.get("status") == "success" and event.get("capability") in ADAPTER_CAPABILITIES
    ]


def extract_strategy_spec(adapter_output: dict[str, Any]) -> dict[str, Any]:
    return (
        adapter_output.get("skill_generation_output", {})
        .get("skill_registry_output", {})
        .get("memory_output", {})
        .get("rag_output", {})
        .get("strategy_spec", {})
    )


def extract_memory_output(adapter_output: dict[str, Any]) -> dict[str, Any]:
    return (
        adapter_output.get("skill_generation_output", {})
        .get("skill_registry_output", {})
        .get("memory_output", {})
    )


def extract_skill_registry_output(adapter_output: dict[str, Any]) -> dict[str, Any]:
    return adapter_output.get("skill_generation_output", {}).get("skill_registry_output", {})


def resolve_run_status(blocked_nodes: list[dict[str, Any]], waiting_nodes: list[dict[str, Any]]) -> str:
    if blocked_nodes:
        return "blocked"
    if waiting_nodes:
        return "waiting_human_confirmation"
    return "completed"


def build_final_output(nodes: list[ResearchDagNode], status: str, adapter_output: dict[str, Any]) -> dict[str, Any]:
    completed_nodes = [node.node_id for node in nodes if node.status == "completed"]
    blocked_nodes = [
        {"node_id": node.node_id, "reason": node.blocked_reason}
        for node in nodes
        if node.status == "blocked"
    ]
    waiting_nodes = [
        {"node_id": node.node_id, "required_confirmations": node.produced_outputs.get("required_confirmations", [])}
        for node in nodes
        if node.status == "waiting_human_confirmation"
    ]
    return {
        "summary": build_summary(status),
        "completed_nodes": completed_nodes,
        "blocked_nodes": blocked_nodes,
        "waiting_human_confirmation_nodes": waiting_nodes,
        "evidence_summary": {
            "adapter_mode": adapter_output.get("adapter_mode"),
            "adapter_trace_count": len(adapter_output.get("adapter_trace", [])),
            "evidence_is_mock": True,
        },
        "allowed_next_steps": ["prepare Lab 10 mock evidence report draft after human review"],
        "not_allowed_actions": ["automatic trading", "unreviewed publication", "automatic skill activation"],
        "next_lab": "Lab 10 Evidence Report",
    }


def build_summary(status: str) -> str:
    if status == "waiting_human_confirmation":
        return "Research Planner DAG reached the human review gate and is waiting for confirmation."
    if status == "blocked":
        return "Research Planner DAG stopped because at least one required node was blocked."
    return "Research Planner DAG completed without human-gated actions."


def contains_prohibited_output_key(value: Any) -> bool:
    if isinstance(value, dict):
        if PROHIBITED_OUTPUT_KEYS.intersection(value):
            return True
        return any(contains_prohibited_output_key(child) for child in value.values())
    if isinstance(value, list):
        return any(contains_prohibited_output_key(child) for child in value)
    return False


def block_planner_for_prohibited_output(nodes: list[ResearchDagNode], planner_trace: list[dict[str, Any]]) -> None:
    node = next((item for item in nodes if item.node_id == "human_review_gate"), nodes[-1])
    set_node_state(
        node,
        "blocked",
        deepcopy(node.produced_outputs),
        "prohibited output field detected",
    )
    planner_trace.append(
        build_trace_event(
            node,
            get_dependency_statuses(nodes, node),
            "safety_check",
            "Planner blocked because a prohibited output field was detected.",
        )
    )
