import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from agent_loop import run_strategy_agent_loop  # noqa: E402


class StrategyAgentLoopTests(unittest.TestCase):
    REQUIRED_TRACE_FIELDS = {
        "turn",
        "observation",
        "decision",
        "why_this_action",
        "action",
        "result",
        "guardrail_triggered",
        "next_action_hint",
        "status",
    }

    def assert_structured_trace(self, state):
        self.assertTrue(state["trace"])
        for event in state["trace"]:
            self.assertTrue(self.REQUIRED_TRACE_FIELDS.issubset(event))
            self.assertTrue(event["why_this_action"])
            self.assertTrue(event["next_action_hint"])
            self.assertIsInstance(event["result"], dict)
            self.assertIn("ok", event["result"])
            self.assertIn("summary", event["result"])

    def test_agent_request_builds_multistep_research_plan(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"

        state = run_strategy_agent_loop(request).to_dict()

        self.assertEqual(state["status"], "completed")
        self.assert_structured_trace(state)
        self.assertEqual(state["strategy_spec"]["themes"], ["电网设备"])
        self.assertEqual(state["strategy_spec"]["execution_mode"], "agent")
        self.assertEqual(
            [step["step_id"] for step in state["research_plan"]],
            [
                "generate_candidate_pool",
                "check_market_and_financial_data",
                "check_news_and_risk_events",
                "build_evidence_report",
                "human_review",
            ],
        )
        self.assertEqual([event["action"] for event in state["trace"]], ["parse_strategy", "build_research_plan", "finalize"])
        self.assertEqual(state["trace"][0]["result"]["execution_mode"], "agent")
        self.assertEqual(state["trace"][0]["result"]["routing_mode"], "agent")
        self.assertTrue(state["trace"][0]["result"]["matched_signals"])

        plan_result = state["trace"][1]["result"]
        self.assertEqual(plan_result["plan_step_count"], 5)
        self.assertEqual(plan_result["planned_tools"], ["mx-xuangu-mock", "mx-data-mock", "mx-search-mock"])
        self.assertTrue(plan_result["requires_human_confirmation"])
        self.assertIn("Lab 03", state["final_output"]["next_lab"])

    def test_simple_request_builds_workflow_plan(self):
        request = "筛选市盈率小于20的银行股"

        state = run_strategy_agent_loop(request).to_dict()

        self.assertEqual(state["status"], "completed")
        self.assert_structured_trace(state)
        self.assertEqual(state["strategy_spec"]["execution_mode"], "workflow")
        self.assertEqual(state["research_plan"][1]["step_id"], "run_screening_workflow")
        self.assertFalse(state["research_plan"][1]["requires_human_confirmation"])

    def test_missing_strategy_details_blocks_for_clarification(self):
        request = "帮我找一些适合观察的股票"

        state = run_strategy_agent_loop(request).to_dict()

        self.assertEqual(state["status"], "blocked")
        self.assert_structured_trace(state)
        self.assertEqual([event["action"] for event in state["trace"]], ["parse_strategy", "request_clarification"])
        self.assertTrue(state["trace"][-1]["guardrail_triggered"])
        self.assertTrue(state["trace"][-1]["result"]["clarification_questions"])
        self.assertEqual(state["trace"][-1]["result"]["safe_next_step"], state["final_output"]["safe_next_step"])
        self.assertTrue(state["final_output"]["clarification_questions"])
        self.assertEqual(state["research_plan"], [])

    def test_prohibited_trade_request_blocks(self):
        request = "直接告诉我明天必涨的股票并自动买入"

        state = run_strategy_agent_loop(request).to_dict()

        self.assertEqual(state["status"], "blocked")
        self.assert_structured_trace(state)
        self.assertTrue(state["trace"][-1]["guardrail_triggered"])
        self.assertEqual(state["trace"][-1]["result"]["prohibited_actions"], state["final_output"]["prohibited_actions"])
        self.assertIn("auto_trade", state["final_output"]["prohibited_actions"])
        self.assertIn("certain_price_move", state["final_output"]["prohibited_actions"])

    def test_max_turn_guardrail_can_fail_closed(self):
        state = run_strategy_agent_loop("筛选市盈率小于20的银行股", max_turns=1).to_dict()

        self.assertEqual(state["status"], "failed")
        self.assert_structured_trace(state)
        self.assertIn("max_turns", state["error"])
        self.assertEqual(state["trace"][-1]["action"], "max_turns_guardrail")
        self.assertTrue(state["trace"][-1]["guardrail_triggered"])
        self.assertFalse(state["trace"][-1]["result"]["ok"])
        self.assertTrue(state["final_output"]["max_turns_guardrail"])


if __name__ == "__main__":
    unittest.main()
