from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from report_model import (  # noqa: E402
    EvidenceReference,
    contains_prohibited_output_key,
    find_prohibited_semantic_paths,
    sanitize_text,
)


class ReportModelTest(unittest.TestCase):
    def test_evidence_reference_serializes_required_fields(self) -> None:
        reference = EvidenceReference(
            evidence_id="ev-001",
            source_type="candidate_evidence",
            source_name="mock_universe.csv",
            source_path="planner_output.mock",
            claim="Mock claim",
            value_summary="Mock value",
            limitations="Mock only",
        ).to_dict()

        self.assertEqual(reference["source_type"], "candidate_evidence")
        self.assertIn("limitations", reference)

    def test_detects_prohibited_output_keys(self) -> None:
        self.assertTrue(contains_prohibited_output_key({"nested": {"buy": True}}))
        self.assertFalse(contains_prohibited_output_key({"nested": {"allowed": True}}))

    def test_sanitize_text_redacts_prohibited_semantics(self) -> None:
        sanitized = sanitize_text("明天必涨并自动买入")

        self.assertNotIn("必涨", sanitized)
        self.assertNotIn("自动买入", sanitized)

    def test_semantic_scan_detects_unsafe_text(self) -> None:
        paths = find_prohibited_semantic_paths({"content": "保证收益"})

        self.assertEqual(paths, ["$.content"])


if __name__ == "__main__":
    unittest.main()
