import os
import sys
import unittest
from copy import deepcopy
from typing import Any


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from run_lab import run_user_preference_memory  # noqa: E402


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
    def test_run_lab_generates_memory_outputs(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_user_preference_memory(request=request, user_id="conservative_user")

        self.assertEqual(result["status"], "completed")
        self.assertIn("memory_snapshot", result)
        self.assertIn("memory_trace", result)
        self.assertIn("preference_application", result)
        self.assertTrue(result["preference_adjusted_evidence"])
        self.assertEqual(result["final_output"]["adjusted_candidate_count"], 1)
        self.assertIn("risk_disclosure", result)
        self.assertIn("Lab 06", result["next_lab"])
        self.assertFalse(PROHIBITED_OUTPUT_KEYS.intersection(collect_keys(result)))

    def test_original_candidate_evidence_is_not_modified(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_user_preference_memory(request=request, user_id="conservative_user")
        original = deepcopy(result["rag_output"]["candidate_evidence"])

        self.assertEqual(result["rag_output"]["candidate_evidence"], original)
        self.assertNotEqual(len(result["preference_adjusted_evidence"]), len(original))

    def test_balanced_user_keeps_two_candidates(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_user_preference_memory(request=request, user_id="balanced_user")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["final_output"]["adjusted_candidate_count"], 2)
        self.assertEqual(result["final_output"]["report_style"], "balanced_evidence_table")

    def test_blocked_request_remains_blocked(self):
        result = run_user_preference_memory(request="直接告诉我明天必涨的股票并自动买入。", user_id="balanced_user")

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["preference_adjusted_evidence"], [])
        self.assertTrue(any(item["step"] == "skip_preference_adjustment" for item in result["memory_trace"]))
        self.assertIn("risk_disclosure", result["final_output"])
        self.assertFalse(PROHIBITED_OUTPUT_KEYS.intersection(collect_keys(result)))


if __name__ == "__main__":
    unittest.main()
