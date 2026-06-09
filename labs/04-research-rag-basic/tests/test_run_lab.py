import os
import sys
import unittest
from typing import Any


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from run_lab import run_research_rag_basic  # noqa: E402


PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value.keys())
        for child in value.values():
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


class RunLabTests(unittest.TestCase):
    def test_run_lab_generates_retrieved_context_and_trace(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_research_rag_basic(request)

        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["candidate_evidence"])
        self.assertTrue(result["retrieval_trace"])
        self.assertTrue(result["retrieved_context"])
        self.assertTrue(result["augmented_evidence"][0]["retrieved_context_refs"])
        self.assertIn("Lab 05", result["next_lab"])
        self.assertIn("risk_disclosure", result)
        self.assertFalse(PROHIBITED_OUTPUT_KEYS.intersection(collect_keys(result)))

    def test_each_retrieved_context_has_required_fields(self):
        result = run_research_rag_basic()

        for item in result["retrieved_context"]:
            self.assertIn("source", item)
            self.assertIn("chunk_id", item)
            self.assertIn("matched_terms", item)
            self.assertIn("used_for", item)
            self.assertTrue(item["matched_terms"])
            self.assertIn(item["used_for"], {"strategy_rule", "risk_boundary", "report_structure"})

    def test_blocked_request_skips_normal_retrieval(self):
        result = run_research_rag_basic("直接告诉我明天必涨的股票并自动买入")

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["candidate_evidence"], [])
        self.assertEqual(result["retrieved_context"], [])
        self.assertEqual(result["retrieval_trace"][0]["step"], "skip_retrieval")
        self.assertIn("risk_disclosure", result["final_output"])
        self.assertFalse(PROHIBITED_OUTPUT_KEYS.intersection(collect_keys(result)))

    def test_user_profile_none_preserves_default_preferences(self):
        result = run_research_rag_basic(user_profile=None)

        self.assertEqual(result["strategy_spec"]["user_preferences"]["max_candidates"], 10)

    def test_user_profile_is_passed_to_lab03(self):
        result = run_research_rag_basic(user_profile={"max_candidates": 1, "risk_level": "low"})

        self.assertEqual(result["strategy_spec"]["user_preferences"]["max_candidates"], 1)
        self.assertEqual(result["strategy_spec"]["user_preferences"]["risk_level"], "low")


if __name__ == "__main__":
    unittest.main()
