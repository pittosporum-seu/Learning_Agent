from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from report_builder import build_report_from_planner  # noqa: E402
from test_evidence_collector import minimal_planner_output  # noqa: E402


class ReportBuilderTest(unittest.TestCase):
    def test_builds_report_with_all_core_sections(self) -> None:
        result = build_report_from_planner(minimal_planner_output())
        sections = result["evidence_report"]["sections"]

        self.assertEqual(result["status"], "needs_human_review")
        self.assertEqual(len(sections), 9)
        self.assertIn("candidate_observation_pool", sections)
        self.assertIn("evidence_table", sections)
        self.assertEqual(result["next_lab"], "Lab 11 Simulation Portfolio")

    def test_generation_trace_covers_each_section(self) -> None:
        result = build_report_from_planner(minimal_planner_output())
        trace_sections = {item["output_section"] for item in result["report_generation_trace"]}

        self.assertEqual(trace_sections, set(result["evidence_report"]["sections"]))

    def test_blocked_planner_creates_blocked_report_and_gaps(self) -> None:
        planner_output = minimal_planner_output()
        planner_output["status"] = "blocked"
        planner_output["blocked_nodes"] = [{"node_id": "adapter_capability_check", "blocked_reason": "upstream blocked"}]
        result = build_report_from_planner(planner_output)
        gaps = result["evidence_report"]["sections"]["risk_and_limitations"]["content"]["evidence_gaps"]

        self.assertEqual(result["status"], "blocked")
        self.assertTrue(gaps)


if __name__ == "__main__":
    unittest.main()
