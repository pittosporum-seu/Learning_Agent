from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from report_builder import build_report_from_planner  # noqa: E402
from report_safety import review_report_output  # noqa: E402
from test_evidence_collector import minimal_planner_output  # noqa: E402


class ReportSafetyTest(unittest.TestCase):
    def test_review_passes_valid_report(self) -> None:
        report_output = build_report_from_planner(minimal_planner_output())
        review = review_report_output(report_output)

        self.assertEqual(review["status"], "passed")

    def test_review_detects_missing_risk_disclosure(self) -> None:
        report_output = build_report_from_planner(minimal_planner_output())
        report_output["risk_disclosure"] = ""
        report_output["evidence_report"]["risk_and_limitations"]["risk_disclosure"] = ""
        review = review_report_output(report_output)
        issue_codes = {item["code"] for item in review["issues"]}

        self.assertIn("missing_risk_disclosure", issue_codes)

    def test_review_detects_prohibited_output_keys(self) -> None:
        report_output = build_report_from_planner(minimal_planner_output())
        report_output["evidence_report"]["sections"]["bad_section"] = {"target_price": "not allowed"}
        review = review_report_output(report_output)
        issue_codes = {item["code"] for item in review["issues"]}

        self.assertIn("prohibited_output_key", issue_codes)

    def test_review_detects_prohibited_semantics(self) -> None:
        report_output = build_report_from_planner(minimal_planner_output())
        report_output["evidence_report"]["sections"]["risk_and_limitations"]["content"]["uncertainty_notes"].append("保证收益")
        review = review_report_output(report_output)
        issue_codes = {item["code"] for item in review["issues"]}

        self.assertIn("prohibited_semantic_text", issue_codes)


if __name__ == "__main__":
    unittest.main()
