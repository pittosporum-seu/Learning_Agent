from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from mock_mx_adapter import MockMXAdapter  # noqa: E402


STRATEGY_SPEC = {
    "themes": ["电网设备"],
    "candidate_rules": ["趋势较强", "回撤较低"],
    "risk_filters": ["没有明显负面新闻"],
    "user_preferences": {"max_candidates": 2},
}


class MockMXAdapterTest(unittest.TestCase):
    def test_mock_adapter_calls_mx_xuangu(self) -> None:
        result = MockMXAdapter().call("mx-xuangu", {"strategy_spec": STRATEGY_SPEC})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["capability"], "mx-xuangu")
        self.assertGreaterEqual(len(result["output"]["candidates"]), 1)

    def test_mock_adapter_calls_mx_data_and_mx_search(self) -> None:
        adapter = MockMXAdapter()
        xuangu = adapter.call("mx-xuangu", {"strategy_spec": STRATEGY_SPEC})
        candidate_ids = [item["candidate_id"] for item in xuangu["output"]["candidates"]]

        data_result = adapter.call("mx-data", {"candidate_ids": candidate_ids})
        search_result = adapter.call("mx-search", {"candidate_ids": candidate_ids})

        self.assertEqual(data_result["status"], "success")
        self.assertIn("market_items", data_result["output"])
        self.assertEqual(search_result["status"], "success")
        self.assertIn("risk_flags", search_result["output"])


if __name__ == "__main__":
    unittest.main()
