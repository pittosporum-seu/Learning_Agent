from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
LAB06_SRC_DIR = LAB_ROOT.parents[0] / "06-skill-registry" / "src"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(LAB06_SRC_DIR))

from run_lab import run_skill_registry  # noqa: E402
from skill_draft_builder import build_skill_draft  # noqa: E402


NORMAL_REQUEST = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。"


class SkillDraftBuilderTest(unittest.TestCase):
    def test_builder_generates_required_draft_fields(self) -> None:
        registry_output = run_skill_registry(request=NORMAL_REQUEST, user_id="balanced_user")
        result = build_skill_draft(registry_output)
        draft = result["generated_skill_draft"]

        for field in [
            "name",
            "description",
            "trigger_scenarios",
            "disabled_scenarios",
            "inputs",
            "outputs",
            "workflow_steps",
            "human_confirmation_points",
            "safety_boundaries",
            "test_cases",
        ]:
            self.assertIn(field, draft)
            self.assertTrue(draft[field])

    def test_skill_draft_markdown_contains_draft_marker(self) -> None:
        registry_output = run_skill_registry(request=NORMAL_REQUEST, user_id="balanced_user")
        result = build_skill_draft(registry_output)

        self.assertIn("DRAFT", result["skill_draft_markdown"])
        self.assertIn("DRAFT ONLY", result["skill_draft_markdown"])


if __name__ == "__main__":
    unittest.main()
