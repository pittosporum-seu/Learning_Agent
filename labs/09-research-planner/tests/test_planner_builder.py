from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from planner_builder import REQUIRED_NODE_IDS, build_research_dag  # noqa: E402


def sample_adapter_output() -> dict:
    return {
        "status": "completed",
        "adapter_mode": "mock-finance",
        "provider_mode": "mock",
        "registered_adapters": [],
        "safety_gate": {"real_provider_allowed": False},
        "adapter_trace": [],
        "skill_generation_output": {"status": "completed"},
        "risk_disclosure": "Mock risk disclosure.",
    }


class PlannerBuilderTest(unittest.TestCase):
    def test_builder_generates_all_required_nodes(self) -> None:
        nodes = build_research_dag(sample_adapter_output())
        node_ids = [node.node_id for node in nodes]

        self.assertEqual(node_ids, REQUIRED_NODE_IDS)
        self.assertTrue(all(node.status == "pending" for node in nodes))

    def test_builder_injects_adapter_context(self) -> None:
        nodes = build_research_dag(sample_adapter_output())

        for node in nodes:
            self.assertEqual(node.context["adapter_mode"], "mock-finance")
            self.assertEqual(node.context["provider_mode"], "mock")
            self.assertTrue(node.context["risk_disclosure_present"])


if __name__ == "__main__":
    unittest.main()
