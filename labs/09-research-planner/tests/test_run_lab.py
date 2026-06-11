from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import run_research_planner_dag  # noqa: E402


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


class RunResearchPlannerDagTest(unittest.TestCase):
    def test_run_lab_normal_request_waits_for_human_confirmation(self) -> None:
        result = run_research_planner_dag(request=NORMAL_REQUEST, user_id="balanced_user")
        statuses = {node["node_id"]: node["status"] for node in result["research_dag"]}

        self.assertEqual(result["status"], "waiting_human_confirmation")
        self.assertEqual(statuses["human_review_gate"], "waiting_human_confirmation")
        self.assertIn("risk_disclosure", result)
        self.assertEqual(result["next_lab"], "Lab 10 Evidence Report")

    def test_run_lab_blocked_request_propagates_to_dag(self) -> None:
        result = run_research_planner_dag(request=BLOCKED_REQUEST)
        statuses = {node["node_id"]: node["status"] for node in result["research_dag"]}

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(statuses["adapter_capability_check"], "blocked")
        self.assertEqual(statuses["candidate_generation"], "skipped")
        self.assertNotIn("completed", [statuses["candidate_generation"], statuses["human_review_gate"]])

    def test_output_has_no_prohibited_keys(self) -> None:
        result = run_research_planner_dag(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse(PROHIBITED_KEYS.intersection(collect_keys(result)))

    def test_does_not_create_runtime_config_directories(self) -> None:
        run_research_planner_dag(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse((REPO_ROOT / ".agents").exists())
        self.assertFalse((REPO_ROOT / ".codex").exists())


if __name__ == "__main__":
    unittest.main()
