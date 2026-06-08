import json
import os
import sys
import unittest
from unittest.mock import patch


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from llm_strategy_intake import (  # noqa: E402
    DEFAULT_XIAOMI_BASE_URL,
    DEFAULT_XIAOMI_CHAT_URL,
    DEFAULT_XIAOMI_MODEL,
    LLMConfig,
    LLMConfigError,
    build_chat_url,
    get_llm_status,
    parse_json_object,
    parse_strategy_request_with_llm,
)


class LLMStrategyIntakeTests(unittest.TestCase):
    def test_env_config_uses_llm_values(self):
        env = {
            "LLM_API_KEY": "llm-key",
            "LLM_BASE_URL": "https://gateway.example/v1",
            "LLM_MODEL": "custom-model",
            "LLM_PROVIDER_LABEL": "Custom Gateway",
            "XIAOMI_API_KEY": "xiaomi-key",
            "XIAOMI_BASE_URL": "https://token-plan-sgp.xiaomimimo.com/v1",
            "XIAOMI_MODEL": "mimo-v2.5",
        }

        config = LLMConfig.from_env(env)

        self.assertEqual(config.api_key, "llm-key")
        self.assertEqual(config.chat_url, "https://gateway.example/v1/chat/completions")
        self.assertEqual(config.model, "custom-model")
        self.assertEqual(config.provider_label, "Custom Gateway")

    def test_env_config_uses_xiaomi_values_as_compatibility_defaults(self):
        with patch.dict(os.environ, {"XIAOMI_API_KEY": "test-key"}, clear=True):
            config = LLMConfig.from_env()

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.chat_url, DEFAULT_XIAOMI_CHAT_URL)
        self.assertEqual(config.model, DEFAULT_XIAOMI_MODEL)
        self.assertEqual(config.provider_label, "Xiaomi MiMo")

    def test_xiaomi_env_aliases_take_precedence_over_legacy_mimo_aliases(self):
        env = {
            "MIMO_API_KEY": "old-key",
            "XIAOMI_API_KEY": "xiaomi-key",
            "MIMO_BASE_URL": "https://wrong.example/v1",
            "XIAOMI_BASE_URL": "https://token-plan-sgp.xiaomimimo.com/v1",
            "MIMO_MODEL": "wrong-model",
            "XIAOMI_MODEL": "mimo-v2.5",
        }

        config = LLMConfig.from_env(env)

        self.assertEqual(config.api_key, "xiaomi-key")
        self.assertEqual(config.chat_url, "https://token-plan-sgp.xiaomimimo.com/v1/chat/completions")
        self.assertEqual(config.model, "mimo-v2.5")

    def test_build_chat_url_accepts_base_or_exact_endpoint(self):
        self.assertEqual(build_chat_url(DEFAULT_XIAOMI_BASE_URL), DEFAULT_XIAOMI_CHAT_URL)
        self.assertEqual(build_chat_url(DEFAULT_XIAOMI_CHAT_URL), DEFAULT_XIAOMI_CHAT_URL)

    def test_missing_key_reports_unconfigured_status(self):
        with patch.dict(os.environ, {}, clear=True):
            status = get_llm_status()

        self.assertFalse(status["configured"])
        self.assertEqual(status["api_key"], "missing")
        with self.assertRaises(LLMConfigError):
            LLMConfig.from_env({})

    def test_llm_response_merges_with_baseline_and_safety_fields(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
        config = LLMConfig(api_key="test-key", chat_url="https://example.test/v1/chat/completions", model="llm-test")

        def fake_transport(url, headers, payload, timeout_seconds):
            self.assertEqual(url, config.chat_url)
            self.assertEqual(headers["api-key"], "test-key")
            self.assertEqual(headers["Authorization"], "Bearer test-key")
            self.assertEqual(payload["model"], "llm-test")
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

        result = parse_strategy_request_with_llm(request, config=config, transport=fake_transport)

        self.assertEqual(result["provider"], "llm")
        self.assertEqual(result["provider_label"], "OpenAI-compatible")
        self.assertEqual(result["model"], "llm-test")
        self.assertEqual(result["usage"]["total_tokens"], 10)
        self.assertEqual(result["strategy_spec"]["market"], "A股")
        self.assertEqual(result["strategy_spec"]["themes"], ["电网设备"])
        self.assertTrue(result["strategy_spec"]["requires_agent"])
        self.assertEqual(result["strategy_spec"]["routing_decision"]["mode"], "agent")
        self.assertIn("time_sensitive", result["strategy_spec"]["routing_decision"]["matched_signals"])
        self.assertIn("不构成投资建议", result["strategy_spec"]["risk_disclosure"])
        self.assertNotIn("stocks", result["strategy_spec"])
        self.assertNotIn("recommendations", result["strategy_spec"])

    def test_empty_model_fields_do_not_override_baseline(self):
        request = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
        config = LLMConfig(api_key="test-key", chat_url="https://example.test/v1/chat/completions", model="llm-test")

        def fake_transport(url, headers, payload, timeout_seconds):
            model_spec = {
                "themes": [],
                "horizon_days": None,
                "candidate_rules": [],
                "risk_filters": [],
                "execution_mode": "agent",
            }
            return {"choices": [{"message": {"content": json.dumps(model_spec, ensure_ascii=False)}}]}

        result = parse_strategy_request_with_llm(request, config=config, transport=fake_transport)

        self.assertEqual(result["strategy_spec"]["themes"], ["电网设备"])
        self.assertEqual(result["strategy_spec"]["horizon_days"], 60)
        self.assertIn("近60日趋势较强", result["strategy_spec"]["candidate_rules"])
        self.assertIn("近期无重大负面新闻", result["strategy_spec"]["risk_filters"])

    def test_markdown_wrapped_json_can_be_parsed(self):
        parsed = parse_json_object('```json\n{"execution_mode": "workflow"}\n```')

        self.assertEqual(parsed["execution_mode"], "workflow")


if __name__ == "__main__":
    unittest.main()
