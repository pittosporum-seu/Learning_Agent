from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import run_skill_registry  # noqa: E402


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


class RunSkillRegistryTest(unittest.TestCase):
    def test_normal_request_generates_selection_outputs(self) -> None:
        result = run_skill_registry(request=NORMAL_REQUEST, user_id="balanced_user")
        selected_names = {skill["name"] for skill in result["selected_skills"]}

        self.assertEqual(result["status"], "completed")
        self.assertIn("memory_output", result)
        self.assertIn("skill_selection_trace", result)
        self.assertIn("candidate-evidence-summary", selected_names)
        self.assertIn("negative-news-risk-review", selected_names)
        self.assertIn("risk_disclosure", result)
        self.assertIn("Lab 07", result["next_lab"])

    def test_blocked_request_does_not_select_execution_skills(self) -> None:
        result = run_skill_registry(request=BLOCKED_REQUEST)
        selected_types = {skill["skill_type"] for skill in result["selected_skills"]}

        self.assertEqual(result["status"], "blocked")
        self.assertFalse({"handoff", "execution_plan"}.intersection(selected_types))

    def test_output_has_no_prohibited_keys(self) -> None:
        result = run_skill_registry(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse(PROHIBITED_KEYS.intersection(collect_keys(result)))


if __name__ == "__main__":
    unittest.main()
