import json
import os
import sys
import unittest
from unittest.mock import patch


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from mimo_strategy_intake import (  # noqa: E402
    DEFAULT_MIMO_CHAT_URL,
    DEFAULT_MIMO_MODEL,
    MimoConfig,
    MimoConfigError,
    get_mimo_status,
    parse_json_object,
    parse_strategy_request_with_mimo,
)


class MimoStrategyIntakeTests(unittest.TestCase):
    def test_env_config_uses_xiaomi_key_and_defaults(self):
        with patch.dict(os.environ, {"XIAOMI_API_KEY": "test-key"}, clear=True):
            config = MimoConfig.from_env()

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.chat_url, DEFAULT_MIMO_CHAT_URL)
        self.assertEqual(config.model, DEFAULT_MIMO_MODEL)

    def test_missing_key_reports_unconfigured_status(self):
        with patch.dict(os.environ, {}, clear=True):
            status = get_mimo_status()

        self.assertFalse(status["configured"])
        self.assertEqual(status["api_key"], "missing")
        with self.assertRaises(MimoConfigError):
            MimoConfig.from_env({})

    def test_mimo_response_merges_with_baseline_and_safety_fields(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
        config = MimoConfig(api_key="test-key", chat_url="https://example.test/v1/chat/completions", model="mimo-test")

        def fake_transport(url, headers, payload, timeout_seconds):
            self.assertEqual(url, config.chat_url)
            self.assertEqual(headers["api-key"], "test-key")
            self.assertEqual(headers["Authorization"], "Bearer test-key")
            self.assertEqual(payload["model"], "mimo-test")
            self.assertGreater(timeout_seconds, 0)
            model_spec = {
                "market": "A股",
                "themes": ["电网设备"],
                "horizon_days": 60,
                "candidate_rules": ["近60日趋势较强", "最大回撤较低"],
                "risk_filters": ["近期无重大负面新闻", "排除 ST / *ST"],
                "output": "候选观察池和证据化报告",
                "execution_mode": "agent",
                "requires_agent": True,
                "assumptions": ["不输出个股买卖建议。"],
                "clarification_questions": [],
                "prohibited_actions": [],
            }
            return {"choices": [{"message": {"content": json.dumps(model_spec, ensure_ascii=False)}}], "usage": {"total_tokens": 10}}

        result = parse_strategy_request_with_mimo(request, config=config, transport=fake_transport)

        self.assertEqual(result["provider"], "mimo")
        self.assertEqual(result["model"], "mimo-test")
        self.assertEqual(result["usage"]["total_tokens"], 10)
        self.assertEqual(result["strategy_spec"]["market"], "A股")
        self.assertEqual(result["strategy_spec"]["themes"], ["电网设备"])
        self.assertTrue(result["strategy_spec"]["requires_agent"])
        self.assertIn("不构成投资建议", result["strategy_spec"]["risk_disclosure"])
        self.assertNotIn("stocks", result["strategy_spec"])
        self.assertNotIn("recommendations", result["strategy_spec"])

    def test_markdown_wrapped_json_can_be_parsed(self):
        parsed = parse_json_object('```json\n{"execution_mode": "workflow"}\n```')

        self.assertEqual(parsed["execution_mode"], "workflow")


if __name__ == "__main__":
    unittest.main()
