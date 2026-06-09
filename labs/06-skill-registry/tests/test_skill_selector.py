from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from skill_registry import build_default_registry  # noqa: E402
from skill_selector import select_skills  # noqa: E402


def sample_memory_output() -> dict:
    return {
        "status": "completed",
        "memory_snapshot": {"user_id": "balanced_user"},
        "preference_adjusted_evidence": [
            {
                "candidate_id": "MOCK_GRID_001",
                "risk_flags": [],
                "sources": ["mock_universe.csv", "mock_prices.csv"],
            }
        ],
        "rag_output": {
            "strategy_spec": {
                "original_request": "生成候选观察池",
                "output": "候选观察池",
                "execution_mode": "mock_research",
            },
            "candidate_evidence": [
                {
                    "candidate_id": "MOCK_GRID_001",
                    "risk_flags": ["valuation_watch"],
                    "sources": ["mock_universe.csv", "mock_prices.csv"],
                }
            ],
            "retrieved_context": [
                {
                    "chunk_id": "risk_policy-001",
                    "source": "risk_policy.md",
                    "matched_terms": ["negative_news"],
                    "used_for": "risk_boundary",
                }
            ],
            "risk_disclosure": "仅用于教学演示，不构成投资建议。",
        },
        "risk_disclosure": "仅用于教学演示，不构成投资建议。",
    }


class SkillSelectorTest(unittest.TestCase):
    def test_normal_request_selects_summary_and_risk_review(self) -> None:
        result = select_skills(sample_memory_output(), build_default_registry())
        selected_names = {skill["name"] for skill in result["selected_skills"]}

        self.assertIn("candidate-evidence-summary", selected_names)
        self.assertIn("negative-news-risk-review", selected_names)

    def test_handoff_skill_requires_human_confirmation_when_selected_or_disabled(self) -> None:
        result = select_skills(sample_memory_output(), build_default_registry())
        all_skills = result["selected_skills"] + result["disabled_skills"]
        handoff = next(skill for skill in all_skills if skill["name"] == "watchlist-handoff")

        self.assertTrue(handoff["requires_human_confirmation"])

    def test_blocked_request_does_not_select_execution_skills(self) -> None:
        blocked_output = sample_memory_output()
        blocked_output["status"] = "blocked"
        blocked_output["preference_adjusted_evidence"] = []
        blocked_output["rag_output"]["candidate_evidence"] = []

        result = select_skills(blocked_output, build_default_registry())
        selected_types = {skill["skill_type"] for skill in result["selected_skills"]}

        self.assertFalse({"handoff", "execution_plan"}.intersection(selected_types))

    def test_missing_risk_disclosure_disables_handoff_and_simulation(self) -> None:
        memory_output = copy.deepcopy(sample_memory_output())
        memory_output["risk_disclosure"] = ""
        memory_output["rag_output"]["risk_disclosure"] = ""

        result = select_skills(memory_output, build_default_registry())
        disabled = {skill["name"]: skill["disabled_reasons"] for skill in result["disabled_skills"]}

        self.assertIn("missing_risk_disclosure", disabled["watchlist-handoff"])
        self.assertIn("missing_risk_disclosure", disabled["simulation-portfolio-plan"])


if __name__ == "__main__":
    unittest.main()
