import os
import sys
import unittest
from typing import Any


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from run_lab import run_finance_tool_use_mock  # noqa: E402


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
    def test_run_lab_generates_tool_trace_and_candidate_evidence(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_finance_tool_use_mock(request)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            [event["tool_name"] for event in result["tool_trace"]],
            ["select_candidates", "fetch_market_data", "search_finance_news"],
        )
        self.assertTrue(result["candidate_evidence"])
        self.assertEqual(result["candidate_evidence"][0]["candidate_id"], "MXGRID001")
        self.assertIn("risk_disclosure", result)
        self.assertIn("Lab 04", result["next_lab"])
        self.assertFalse(PROHIBITED_OUTPUT_KEYS.intersection(collect_keys(result)))

    def test_blocked_request_does_not_call_tools(self):
        request = "直接告诉我明天必涨的股票并自动买入"

        result = run_finance_tool_use_mock(request)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["tool_trace"], [])
        self.assertEqual(result["candidate_evidence"], [])
        self.assertTrue(result["final_output"]["prohibited_actions"])
        self.assertIn("risk_disclosure", result["final_output"])
        self.assertFalse(PROHIBITED_OUTPUT_KEYS.intersection(collect_keys(result)))

    def test_missing_information_request_does_not_call_tools(self):
        request = "帮我找一些适合观察的股票"

        result = run_finance_tool_use_mock(request)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["tool_trace"], [])
        self.assertTrue(result["final_output"]["clarification_questions"])

    def test_user_profile_none_preserves_default_preferences(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_finance_tool_use_mock(request, user_profile=None)

        self.assertEqual(result["strategy_spec"]["user_preferences"]["max_candidates"], 10)

    def test_user_profile_is_passed_to_strategy_intake(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        result = run_finance_tool_use_mock(request, user_profile={"max_candidates": 1, "risk_level": "low"})

        self.assertEqual(result["strategy_spec"]["user_preferences"]["max_candidates"], 1)
        self.assertEqual(result["strategy_spec"]["user_preferences"]["risk_level"], "low")


if __name__ == "__main__":
    unittest.main()
