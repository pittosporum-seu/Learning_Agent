from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from planner_builder import build_research_dag  # noqa: E402
from planner_executor import execute_research_planner  # noqa: E402


def normal_adapter_output() -> dict:
    return {
        "status": "completed",
        "adapter_mode": "mock-finance",
        "provider_mode": "mock",
        "registered_adapters": [],
        "safety_gate": {"real_provider_allowed": False},
        "adapter_trace": [
            {
                "adapter_name": "mock-finance",
                "provider_mode": "mock",
                "capability": "candidate-screen",
                "input_summary": {},
                "output": {"candidates": [{"candidate_id": "MXGRID001"}]},
                "status": "success",
                "error": None,
                "requires_api_key": False,
                "requires_human_confirmation": False,
            },
            {
                "adapter_name": "mock-finance",
                "provider_mode": "mock",
                "capability": "market-data",
                "input_summary": {},
                "output": {"market_items": [{"candidate_id": "MXGRID001"}], "missing_candidate_ids": []},
                "status": "success",
                "error": None,
                "requires_api_key": False,
                "requires_human_confirmation": False,
            },
            {
                "adapter_name": "mock-finance",
                "provider_mode": "mock",
                "capability": "finance-news",
                "input_summary": {},
                "output": {"news_items": [{"candidate_id": "MXGRID001"}], "risk_flags": []},
                "status": "success",
                "error": None,
                "requires_api_key": False,
                "requires_human_confirmation": False,
            },
        ],
        "skill_generation_output": {
            "status": "completed",
            "skill_registry_output": {
                "selected_skills": [{"name": "candidate-evidence-summary"}],
                "disabled_skills": [],
                "skill_selection_trace": [{"name": "candidate-evidence-summary"}],
                "memory_output": {
                    "memory_trace": [{"event": "loaded"}],
                    "preference_adjusted_evidence": [{"candidate_id": "MXGRID001"}],
                    "rag_output": {"strategy_spec": {"execution_mode": "agent"}},
                },
            },
        },
        "risk_disclosure": "Mock risk disclosure.",
    }


class PlannerExecutorTest(unittest.TestCase):
    def test_normal_mock_path_waits_for_human_confirmation(self) -> None:
        adapter_output = normal_adapter_output()
        result = execute_research_planner(build_research_dag(adapter_output), adapter_output)
        statuses = {node["node_id"]: node["status"] for node in result["research_dag"]}

        self.assertEqual(result["status"], "waiting_human_confirmation")
        for node_id in [
            "parse_and_route",
            "adapter_capability_check",
            "candidate_generation",
            "market_data_check",
            "news_risk_check",
            "evidence_context_attach",
            "memory_preference_adjustment",
            "skill_selection",
        ]:
            self.assertEqual(statuses[node_id], "completed")
        self.assertEqual(statuses["human_review_gate"], "waiting_human_confirmation")

    def test_upstream_blocked_skips_downstream_nodes(self) -> None:
        adapter_output = normal_adapter_output()
        adapter_output["status"] = "blocked"
        adapter_output["adapter_trace"] = []
        result = execute_research_planner(build_research_dag(adapter_output), adapter_output)
        statuses = {node["node_id"]: node["status"] for node in result["research_dag"]}

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(statuses["adapter_capability_check"], "blocked")
        self.assertEqual(statuses["candidate_generation"], "skipped")
        self.assertEqual(statuses["human_review_gate"], "skipped")

    def test_missing_risk_disclosure_blocks_human_review_gate(self) -> None:
        adapter_output = normal_adapter_output()
        adapter_output.pop("risk_disclosure")
        result = execute_research_planner(build_research_dag(adapter_output), adapter_output)
        statuses = {node["node_id"]: node["status"] for node in result["research_dag"]}

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(statuses["human_review_gate"], "blocked")

    def test_planner_trace_contains_each_node_status_and_reason(self) -> None:
        adapter_output = normal_adapter_output()
        result = execute_research_planner(build_research_dag(adapter_output), adapter_output)

        self.assertEqual(len(result["planner_trace"]), 9)
        for event in result["planner_trace"]:
            self.assertIn("node_id", event)
            self.assertIn("status", event)
            self.assertIn("reason", event)

    def test_external_provider_safety_gate_blocks_adapter_nodes(self) -> None:
        adapter_output = normal_adapter_output()
        adapter_output["adapter_mode"] = "external-finance"
        adapter_output["safety_gate"] = {"real_provider_allowed": False}
        result = execute_research_planner(build_research_dag(adapter_output), adapter_output)
        statuses = {node["node_id"]: node["status"] for node in result["research_dag"]}

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(statuses["adapter_capability_check"], "blocked")
        self.assertEqual(statuses["candidate_generation"], "skipped")

    def test_prohibited_output_field_blocks_planner(self) -> None:
        adapter_output = normal_adapter_output()
        dirty = deepcopy(adapter_output)
        dirty["adapter_trace"][0]["output"]["target_price"] = "not allowed"

        result = execute_research_planner(build_research_dag(dirty), dirty)

        self.assertEqual(result["status"], "blocked")
        self.assertTrue(result["blocked_nodes"])


if __name__ == "__main__":
    unittest.main()
