from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


VALID_STATUSES = {
    "pending",
    "ready",
    "running",
    "completed",
    "blocked",
    "skipped",
    "waiting_human_confirmation",
}


@dataclass
class ResearchDagNode:
    node_id: str
    node_type: str
    depends_on: list[str]
    inputs: list[str]
    outputs: list[str]
    requires_human_confirmation: bool
    failure_behavior: str
    status: str = "pending"
    blocked_reason: str = ""
    skipped_reason: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    produced_outputs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ResearchDagNode":
        status = value.get("status", "pending")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid node status for {value.get('node_id')}: {status}")
        return cls(
            node_id=value["node_id"],
            node_type=value["node_type"],
            depends_on=list(value.get("depends_on", [])),
            inputs=list(value.get("inputs", [])),
            outputs=list(value.get("outputs", [])),
            requires_human_confirmation=bool(value.get("requires_human_confirmation", False)),
            failure_behavior=value["failure_behavior"],
            status=status,
            blocked_reason=value.get("blocked_reason", ""),
            skipped_reason=value.get("skipped_reason", ""),
            context=dict(value.get("context", {})),
            produced_outputs=dict(value.get("produced_outputs", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _node_map(nodes: list[ResearchDagNode]) -> dict[str, ResearchDagNode]:
    mapped: dict[str, ResearchDagNode] = {}
    for node in nodes:
        if node.node_id in mapped:
            raise ValueError(f"Duplicate DAG node: {node.node_id}")
        mapped[node.node_id] = node
    return mapped


def validate_dag_dependencies(nodes: list[ResearchDagNode]) -> None:
    mapped = _node_map(nodes)
    for node in nodes:
        for dependency in node.depends_on:
            if dependency not in mapped:
                raise ValueError(f"Node {node.node_id} depends on missing node: {dependency}")
    topological_sort_nodes(nodes)


def topological_sort_nodes(nodes: list[ResearchDagNode]) -> list[ResearchDagNode]:
    mapped = _node_map(nodes)
    temporary: set[str] = set()
    permanent: set[str] = set()
    ordered: list[ResearchDagNode] = []

    def visit(node_id: str, path: list[str]) -> None:
        if node_id in permanent:
            return
        if node_id in temporary:
            cycle = " -> ".join(path + [node_id])
            raise ValueError(f"DAG contains a cycle: {cycle}")
        if node_id not in mapped:
            raise ValueError(f"DAG references missing node: {node_id}")

        temporary.add(node_id)
        node = mapped[node_id]
        for dependency in node.depends_on:
            visit(dependency, path + [node_id])
        temporary.remove(node_id)
        permanent.add(node_id)
        ordered.append(node)

    for node in nodes:
        visit(node.node_id, [])
    return ordered


def get_dependency_statuses(nodes: list[ResearchDagNode], node: ResearchDagNode) -> dict[str, str]:
    mapped = _node_map(nodes)
    return {dependency: mapped[dependency].status for dependency in node.depends_on}
