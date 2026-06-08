import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from strategy_intake import parse_strategy_request  # noqa: E402


class StrategyIntakeTests(unittest.TestCase):
    def test_default_case_parses_to_agent_spec(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。"

        spec = parse_strategy_request(request).to_dict()

        self.assertEqual(spec["market"], "A股")
        self.assertEqual(spec["themes"], ["半导体", "人工智能"])
        self.assertEqual(spec["horizon_days"], 60)
        self.assertIn("近60日趋势较强", spec["candidate_rules"])
        self.assertIn("最大回撤较低", spec["candidate_rules"])
        self.assertIn("近期无重大负面新闻", spec["risk_filters"])
        self.assertEqual(spec["output"], "候选观察池和证据化报告")
        self.assertEqual(spec["execution_mode"], "agent")
        self.assertTrue(spec["requires_agent"])
        self.assertEqual(spec["routing_decision"]["mode"], "agent")
        self.assertIn("time_sensitive", spec["routing_decision"]["matched_signals"])
        self.assertIn("multi_condition", spec["routing_decision"]["matched_signals"])
        self.assertIn("watchlist_output", spec["routing_decision"]["matched_signals"])
        self.assertIn("Lab 02", spec["routing_decision"]["next_step"])
        self.assertIn("固定筛选流程不足", spec["routing_decision"]["not_selected"]["workflow"])
        self.assertEqual(spec["clarification_questions"], [])
        self.assertIn("不构成投资建议", spec["risk_disclosure"])
        self.assertNotIn("stocks", spec)
        self.assertNotIn("recommendations", spec)

    def test_missing_theme_and_rules_requires_clarification(self):
        request = "帮我找一些适合观察的股票"

        spec = parse_strategy_request(request).to_dict()

        self.assertEqual(spec["execution_mode"], "needs_clarification")
        self.assertFalse(spec["requires_agent"])
        self.assertEqual(spec["routing_decision"]["mode"], "needs_clarification")
        self.assertIn("missing_information", spec["routing_decision"]["matched_signals"])
        self.assertIn("missing_theme", spec["routing_decision"]["matched_signals"])
        self.assertIn("重新解析", spec["routing_decision"]["next_step"])
        self.assertTrue(any("主题或行业" in question for question in spec["clarification_questions"]))
        self.assertTrue(any("观察时间窗口" in question for question in spec["clarification_questions"]))
        self.assertTrue(any("候选筛选规则" in question for question in spec["clarification_questions"]))

    def test_simple_valuation_screen_is_workflow(self):
        request = "筛选市盈率小于20的银行股"

        spec = parse_strategy_request(request).to_dict()

        self.assertEqual(spec["market"], "A股")
        self.assertEqual(spec["themes"], ["银行"])
        self.assertIn("市盈率小于20", spec["candidate_rules"])
        self.assertEqual(spec["execution_mode"], "workflow")
        self.assertFalse(spec["requires_agent"])
        self.assertEqual(spec["routing_decision"]["mode"], "workflow")
        self.assertIn("valuation_filter", spec["routing_decision"]["matched_signals"])
        self.assertIn("deterministic_screening", spec["routing_decision"]["matched_signals"])
        self.assertIn("固定筛选 workflow", spec["routing_decision"]["next_step"])
        self.assertIn("没有近期新闻核验", spec["routing_decision"]["not_selected"]["agent"])

    def test_user_profile_overrides_defaults(self):
        request = "找近 30 日趋势较强的新能源股票"
        profile = {"risk_level": "low", "max_candidates": 5, "exclude_st": True}

        spec = parse_strategy_request(request, user_profile=profile).to_dict()

        self.assertEqual(spec["user_preferences"]["risk_level"], "low")
        self.assertEqual(spec["user_preferences"]["max_candidates"], 5)
        self.assertIn("排除 ST / *ST", spec["risk_filters"])

    def test_power_grid_equipment_theme_parses(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        spec = parse_strategy_request(request).to_dict()

        self.assertEqual(spec["themes"], ["电网设备"])
        self.assertEqual(spec["horizon_days"], 60)
        self.assertIn("近60日趋势较强", spec["candidate_rules"])
        self.assertIn("最大回撤较低", spec["candidate_rules"])
        self.assertIn("近期无重大负面新闻", spec["risk_filters"])
        self.assertEqual(spec["execution_mode"], "agent")
        self.assertEqual(spec["routing_decision"]["mode"], "agent")
        self.assertEqual(spec["clarification_questions"], [])

    def test_prohibited_request_gets_boundary_prompt(self):
        request = "直接告诉我明天必涨的股票并自动买入"

        spec = parse_strategy_request(request).to_dict()

        self.assertEqual(spec["execution_mode"], "needs_clarification")
        self.assertEqual(spec["routing_decision"]["mode"], "blocked")
        self.assertIn("prohibited_intent", spec["routing_decision"]["matched_signals"])
        self.assertIn("prohibited:certain_price_move", spec["routing_decision"]["matched_signals"])
        self.assertIn("prohibited:auto_trade", spec["routing_decision"]["matched_signals"])
        self.assertIn("安全阻断", spec["routing_decision"]["next_step"])
        self.assertIn("certain_price_move", spec["prohibited_actions"])
        self.assertIn("auto_trade", spec["prohibited_actions"])
        self.assertEqual(spec["output"], "风险边界提示和可替代的投研问题")
        self.assertTrue(any("高风险交易" in question for question in spec["clarification_questions"]))


if __name__ == "__main__":
    unittest.main()
