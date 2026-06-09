from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import run_mx_skills_adapter  # noqa: E402


NORMAL_REQUEST = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"
BLOCKED_REQUEST = "直接告诉我明天必涨的股票并自动买入。"
PROHIBITED_KEYS = {"buy", "sell", "recommendation", "target_price"}


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


class RunMXSkillsAdapterTest(unittest.TestCase):
    def test_normal_request_generates_adapter_trace(self) -> None:
        result = run_mx_skills_adapter(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["adapter_mode"], "mock-mx")
        self.assertEqual([event["capability"] for event in result["adapter_trace"]], ["mx-xuangu", "mx-data", "mx-search"])
        self.assertFalse(result["safety_gate"]["real_provider_allowed"])
        self.assertIn("risk_disclosure", result)
        self.assertIn("Lab 09", result["next_lab"])

    def test_blocked_request_does_not_call_adapter(self) -> None:
        result = run_mx_skills_adapter(request=BLOCKED_REQUEST)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["adapter_trace"], [])

    def test_real_stub_mode_is_blocked_by_safety_gate(self) -> None:
        result = run_mx_skills_adapter(request=NORMAL_REQUEST, adapter_mode="real-mx-stub")

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["safety_gate"]["real_provider_allowed"])
        self.assertEqual(result["adapter_trace"][0]["status"], "blocked")

    def test_output_has_no_prohibited_keys(self) -> None:
        result = run_mx_skills_adapter(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse(PROHIBITED_KEYS.intersection(collect_keys(result)))

    def test_does_not_create_runtime_config_directories(self) -> None:
        run_mx_skills_adapter(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse((REPO_ROOT / ".agents").exists())
        self.assertFalse((REPO_ROOT / ".codex").exists())


if __name__ == "__main__":
    unittest.main()
