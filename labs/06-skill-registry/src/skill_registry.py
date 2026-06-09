from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = LAB_ROOT / "data"
SKILLS_PATH = DATA_DIR / "mock_skills.json"


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    description: str
    skill_type: str
    triggers: list[str]
    disabled_when: list[str]
    inputs: list[str]
    outputs: list[str]
    requires_human_confirmation: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillDefinition":
        return cls(
            name=data["name"],
            description=data["description"],
            skill_type=data["skill_type"],
            triggers=list(data.get("triggers", [])),
            disabled_when=list(data.get("disabled_when", [])),
            inputs=list(data.get("inputs", [])),
            outputs=list(data.get("outputs", [])),
            requires_human_confirmation=bool(data.get("requires_human_confirmation", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SkillRegistry:
    def __init__(self, skills: list[SkillDefinition]) -> None:
        self._skills = {skill.name: skill for skill in skills}

    @classmethod
    def from_path(cls, path: Path = SKILLS_PATH) -> "SkillRegistry":
        raw_skills = json.loads(path.read_text(encoding="utf-8"))
        return cls([SkillDefinition.from_dict(item) for item in raw_skills])

    def list_skills(self) -> list[dict[str, Any]]:
        return [skill.to_dict() for skill in self._skills.values()]

    def get_skill(self, name: str) -> SkillDefinition:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise KeyError(f"Unknown mock skill: {name}") from exc

    def iter_skills(self) -> list[SkillDefinition]:
        return list(self._skills.values())


def build_default_registry() -> SkillRegistry:
    return SkillRegistry.from_path()
