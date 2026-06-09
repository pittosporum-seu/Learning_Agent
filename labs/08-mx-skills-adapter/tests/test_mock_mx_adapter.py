from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from mock_mx_adapter import MockFinanceAdapter  # noqa: E402


STRATEGY_SPEC = {
    "themes": ["电网设备"],
    "candidate_rules": ["趋势较强", "回撤较低"],
    "risk_filters": ["没有明显负面新闻"],
    "user_preferences": {"max_candidates": 2},
}


class MockFinanceAdapterTest(unittest.TestCase):
    def test_mock_adapter_calls_candidate_screen(self) -> None:
        result = MockFinanceAdapter().call("candidate-screen", {"strategy_spec": STRATEGY_SPEC})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["capability"], "candidate-screen")
        self.assertGreaterEqual(len(result["output"]["candidates"]), 1)

    def test_mock_adapter_calls_market_data_and_finance_news(self) -> None:
        adapter = MockFinanceAdapter()
        candidate_screen = adapter.call("candidate-screen", {"strategy_spec": STRATEGY_SPEC})
        candidate_ids = [item["candidate_id"] for item in candidate_screen["output"]["candidates"]]

        data_result = adapter.call("market-data", {"candidate_ids": candidate_ids})
        search_result = adapter.call("finance-news", {"candidate_ids": candidate_ids})

        self.assertEqual(data_result["status"], "success")
        self.assertIn("market_items", data_result["output"])
        self.assertEqual(search_result["status"], "success")
        self.assertIn("risk_flags", search_result["output"])

    def test_mock_adapter_accepts_legacy_mx_aliases(self) -> None:
        result = MockFinanceAdapter().call("mx-xuangu", {"strategy_spec": STRATEGY_SPEC})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["capability"], "candidate-screen")


if __name__ == "__main__":
    unittest.main()
