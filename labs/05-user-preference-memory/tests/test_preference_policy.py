import os
import sys
import unittest
from copy import deepcopy


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from memory_store import build_memory_snapshot  # noqa: E402
from preference_policy import apply_preferences, build_effective_user_profile, build_preference_application  # noqa: E402


SAMPLE_EVIDENCE = [
    {
        "candidate_id": "A",
        "candidate_name": "Mock A",
        "theme": "电网设备",
        "risk_flags": [],
        "evidence_items": [{"source_name": "mock_universe.csv"}],
    },
    {
        "candidate_id": "B",
        "candidate_name": "Mock B",
        "theme": "电网设备",
        "risk_flags": ["valuation_watch"],
        "evidence_items": [{"source_name": "mock_news.md"}],
    },
    {
        "candidate_id": "C",
        "candidate_name": "Mock C",
        "theme": "人工智能",
        "risk_flags": ["negative_news"],
        "evidence_items": [{"source_name": "mock_news.md"}],
    },
]


class PreferencePolicyTests(unittest.TestCase):
    def test_effective_user_profile_applies_max_candidates(self):
        snapshot = build_memory_snapshot("conservative_user")

        profile = build_effective_user_profile(snapshot)

        self.assertEqual(profile["max_candidates"], 1)
        self.assertEqual(profile["report_style"], "brief_risk_first")

    def test_apply_preferences_filters_excluded_risk_flags(self):
        profile = {
            "max_candidates": 10,
            "excluded_themes": [],
            "excluded_risk_flags": ["valuation_watch", "negative_news"],
        }

        result = apply_preferences(SAMPLE_EVIDENCE, profile)

        ids = [item["candidate_id"] for item in result["preference_adjusted_evidence"]]
        self.assertEqual(ids, ["A"])
        self.assertTrue(any(item["field"] == "excluded_risk_flags" for item in result["applied"]))

    def test_apply_preferences_does_not_mutate_original_evidence(self):
        original = deepcopy(SAMPLE_EVIDENCE)

        apply_preferences(SAMPLE_EVIDENCE, {"max_candidates": 1, "excluded_risk_flags": ["negative_news"]})

        self.assertEqual(SAMPLE_EVIDENCE, original)

    def test_dangerous_preferences_are_ignored(self):
        snapshot = build_memory_snapshot("conservative_user")

        application = build_preference_application(snapshot)

        ignored_fields = {item["field"] for item in application["ignored"]}
        self.assertIn("risk_disclosure", ignored_fields)
        self.assertIn("skip_guardrails", ignored_fields)
        self.assertTrue(application["safety_notes"])


if __name__ == "__main__":
    unittest.main()
