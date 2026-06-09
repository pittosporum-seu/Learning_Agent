from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from skill_registry import build_default_registry  # noqa: E402


class SkillRegistryTest(unittest.TestCase):
    def test_registry_loads_four_mock_skills(self) -> None:
        registry = build_default_registry()
        names = {skill["name"] for skill in registry.list_skills()}

        self.assertEqual(len(names), 4)
        self.assertEqual(
            names,
            {
                "candidate-evidence-summary",
                "negative-news-risk-review",
                "watchlist-handoff",
                "simulation-portfolio-plan",
            },
        )

    def test_get_skill_finds_candidate_evidence_summary(self) -> None:
        registry = build_default_registry()
        skill = registry.get_skill("candidate-evidence-summary")

        self.assertEqual(skill.name, "candidate-evidence-summary")
        self.assertIn("candidate_evidence", skill.inputs)
        self.assertFalse(skill.requires_human_confirmation)


if __name__ == "__main__":
    unittest.main()
