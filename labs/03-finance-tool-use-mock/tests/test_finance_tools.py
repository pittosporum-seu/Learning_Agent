import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from finance_tools import fetch_market_data, search_finance_news, select_candidates  # noqa: E402


class FinanceToolsTests(unittest.TestCase):
    def test_select_candidates_filters_mock_grid_equipment(self):
        spec = {
            "themes": ["电网设备"],
            "candidate_rules": ["近60日趋势较强", "最大回撤较低"],
            "risk_filters": ["近期无重大负面新闻", "排除 ST / *ST"],
            "user_preferences": {"max_candidates": 10},
        }

        result = select_candidates(spec)

        ids = [item["candidate_id"] for item in result["candidates"]]
        self.assertEqual(ids, ["MXGRID001", "MXGRID002"])
        self.assertNotIn("MXGRID003", ids)

    def test_fetch_market_data_returns_trend_and_drawdown(self):
        result = fetch_market_data(["MXGRID001"])

        item = result["market_items"][0]
        self.assertEqual(item["candidate_id"], "MXGRID001")
        self.assertIn("trend_score", item)
        self.assertIn("max_drawdown", item)
        self.assertGreater(item["trend_score"], 0)

    def test_search_finance_news_returns_risk_flags(self):
        result = search_finance_news(["MXGRID002", "MXGRID003"])

        self.assertTrue(result["news_items"])
        self.assertIn("valuation_watch", result["risk_flags"])
        self.assertIn("negative_news", result["risk_flags"])


if __name__ == "__main__":
    unittest.main()
