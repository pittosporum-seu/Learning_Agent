from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from skill_safety_review import review_skill_draft  # noqa: E402


def valid_draft() -> dict:
    return {
        "name": "candidate-evidence-summary-draft",
        "draft": True,
        "disabled_scenarios": ["missing_risk_disclosure"],
        "human_confirmation_points": ["Human review is required before formal activation."],
        "risk_disclosure": "仅用于教学演示，不构成投资建议。",
    }


class SkillSafetyReviewTest(unittest.TestCase):
    def test_review_requires_human_review_for_valid_draft(self) -> None:
        result = review_skill_draft(valid_draft(), "# candidate-evidence-summary-draft (DRAFT)\nHuman review")

        self.assertEqual(result["status"], "needs_human_review")
        self.assertEqual(result["issues"], [])

    def test_review_checks_disabled_scenarios_risk_disclosure_and_human_confirmation(self) -> None:
        result = review_skill_draft({"name": "unsafe-draft", "draft": True}, "# unsafe-draft")

        self.assertEqual(result["status"], "failed")
        self.assertIn("missing_risk_disclosure", result["issues"])
        self.assertIn("missing_disabled_scenarios", result["issues"])
        self.assertIn("missing_human_review_or_confirmation", result["issues"])

    def test_review_detects_prohibited_output_keys(self) -> None:
        draft = valid_draft()
        draft["target_price"] = "not allowed"

        result = review_skill_draft(draft, "# candidate-evidence-summary-draft (DRAFT)\nHuman review")

        self.assertEqual(result["status"], "failed")
        self.assertIn("prohibited_output_key_present", result["issues"])


if __name__ == "__main__":
    unittest.main()
