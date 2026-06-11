from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from dag_model import ResearchDagNode, topological_sort_nodes, validate_dag_dependencies  # noqa: E402


def node(node_id: str, depends_on: list[str] | None = None) -> ResearchDagNode:
    return ResearchDagNode(
        node_id=node_id,
        node_type="test",
        depends_on=depends_on or [],
        inputs=[],
        outputs=[],
        requires_human_confirmation=False,
        failure_behavior="test failure behavior",
    )


class DagModelTest(unittest.TestCase):
    def test_validate_dag_dependencies_accepts_valid_dag(self) -> None:
        nodes = [node("parse"), node("adapter", ["parse"]), node("candidate", ["adapter"])]

        validate_dag_dependencies(nodes)

    def test_validate_dag_dependencies_rejects_missing_dependency(self) -> None:
        nodes = [node("candidate", ["missing"])]

        with self.assertRaises(ValueError):
            validate_dag_dependencies(nodes)

    def test_validate_dag_dependencies_rejects_cycle(self) -> None:
        nodes = [node("a", ["b"]), node("b", ["a"])]

        with self.assertRaises(ValueError):
            validate_dag_dependencies(nodes)

    def test_topological_sort_respects_dependencies(self) -> None:
        nodes = [node("candidate", ["adapter"]), node("parse"), node("adapter", ["parse"])]

        ordered = [item.node_id for item in topological_sort_nodes(nodes)]

        self.assertEqual(ordered, ["parse", "adapter", "candidate"])


if __name__ == "__main__":
    unittest.main()
