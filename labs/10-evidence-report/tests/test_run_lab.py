from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import run_evidence_report  # noqa: E402


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


class RunEvidenceReportTest(unittest.TestCase):
    def test_normal_request_generates_reviewable_report(self) -> None:
        result = run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")
        report = result["evidence_report"]

        self.assertEqual(result["status"], "needs_human_review")
        self.assertEqual(report["status"], "needs_human_review")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(result["next_lab"], "Lab 11 Simulation Portfolio")
        self.assertEqual(result["report_safety_review"]["status"], "passed")

    def test_report_contains_risk_disclosure(self) -> None:
        result = run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertIn("risk_disclosure", result)
        self.assertTrue(result["risk_disclosure"])
        self.assertTrue(result["evidence_report"]["sections"]["risk_and_limitations"]["content"]["risk_disclosure"])

    def test_each_candidate_observation_has_evidence_refs(self) -> None:
        result = run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")
        observations = result["evidence_report"]["sections"]["candidate_observation_pool"]["content"]

        self.assertTrue(observations)
        self.assertTrue(all(item["evidence_refs"] for item in observations))

    def test_evidence_table_items_have_required_source_fields(self) -> None:
        result = run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")
        evidence_table = result["evidence_report"]["sections"]["evidence_table"]["content"]

        self.assertTrue(evidence_table)
        for item in evidence_table:
            self.assertTrue(item["source_name"])
            self.assertTrue(item["source_type"])
            self.assertIn("limitations", item)

    def test_blocked_request_generates_blocked_report_with_gaps(self) -> None:
        result = run_evidence_report(request=BLOCKED_REQUEST)
        risk_section = result["evidence_report"]["sections"]["risk_and_limitations"]["content"]

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["evidence_report"]["status"], "blocked")
        self.assertTrue(risk_section["evidence_gaps"])

    def test_report_generation_trace_covers_core_sections(self) -> None:
        result = run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")
        trace_sections = {item["output_section"] for item in result["report_generation_trace"]}

        self.assertEqual(trace_sections, set(result["evidence_report"]["sections"]))

    def test_output_has_no_prohibited_keys(self) -> None:
        result = run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse(PROHIBITED_KEYS.intersection(collect_keys(result)))

    def test_does_not_create_runtime_config_directories(self) -> None:
        run_evidence_report(request=NORMAL_REQUEST, user_id="balanced_user")

        self.assertFalse((REPO_ROOT / ".agents").exists())
        self.assertFalse((REPO_ROOT / ".codex").exists())


if __name__ == "__main__":
    unittest.main()
