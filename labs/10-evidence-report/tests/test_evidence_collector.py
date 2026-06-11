from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from evidence_collector import build_candidate_observations, collect_report_inputs  # noqa: E402


def minimal_planner_output() -> dict:
    return {
        "request": "mock request",
        "user_id": "balanced_user",
        "status": "waiting_human_confirmation",
        "adapter_output": {
            "status": "completed",
            "adapter_trace": [
                {
                    "adapter_name": "mock-finance",
                    "capability": "candidate-screen",
                    "status": "success",
                    "output": {"summary": "ok"},
                }
            ],
            "skill_generation_output": {
                "skill_registry_output": {
                    "memory_output": {
                        "preference_adjusted_evidence": [
                            {"candidate_id": "C1"},
                        ],
                        "rag_output": {
                            "strategy_spec": {
                                "themes": ["电网设备"],
                                "horizon_days": 60,
                                "routing_decision": {"mode": "agent"},
                                "output": "mock report",
                            },
                            "candidate_evidence": [
                                {
                                    "candidate_id": "C1",
                                    "candidate_name": "Candidate One",
                                    "theme": "电网设备",
                                    "risk_flags": [],
                                    "evidence_items": [
                                        {
                                            "evidence_id": "C1-market",
                                            "source_type": "mock_market_data",
                                            "source_name": "mock_prices.csv",
                                            "claim": "Market data exists.",
                                            "value": {"trend_score": 80},
                                            "limitations": "Mock only.",
                                            "confidence": "mock",
                                        }
                                    ],
                                }
                            ],
                            "retrieved_context": [
                                {
                                    "source": "report_template.md",
                                    "chunk_id": "report_template-01",
                                    "section": "Report",
                                    "used_for": "report_structure",
                                    "matched_terms": ["report"],
                                    "content": "Mock context",
                                }
                            ],
                        },
                    }
                }
            },
        },
        "research_dag": [{"node_id": "human_review_gate", "status": "waiting_human_confirmation"}],
        "planner_trace": [{"node_id": "human_review_gate", "status": "waiting_human_confirmation", "reason": "review"}],
        "blocked_nodes": [],
        "skipped_nodes": [],
        "waiting_human_confirmation_nodes": [{"node_id": "human_review_gate", "produced_outputs": {}}],
        "risk_disclosure": "risk",
    }


class EvidenceCollectorTest(unittest.TestCase):
    def test_collects_candidate_context_adapter_and_planner_refs(self) -> None:
        collected = collect_report_inputs(minimal_planner_output())
        source_types = {item["source_type"] for item in collected["evidence_refs"]}

        self.assertIn("mock_market_data", source_types)
        self.assertIn("retrieved_context", source_types)
        self.assertIn("adapter_trace", source_types)
        self.assertIn("planner_trace", source_types)

    def test_candidate_observations_keep_evidence_refs(self) -> None:
        observations = build_candidate_observations(
            minimal_planner_output()["adapter_output"]["skill_generation_output"]["skill_registry_output"]["memory_output"]["rag_output"][
                "candidate_evidence"
            ],
            [{"candidate_id": "C1"}],
        )

        self.assertEqual(observations[0]["evidence_refs"], ["C1-market"])
        self.assertEqual(observations[0]["preference_status"], "included_in_adjusted_view")


if __name__ == "__main__":
    unittest.main()
