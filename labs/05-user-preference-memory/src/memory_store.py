from __future__ import annotations

import json
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = LAB_ROOT / "data"
PREFERENCES_PATH = DATA_DIR / "mock_user_preferences.json"
EVENTS_PATH = DATA_DIR / "memory_events.jsonl"


class UnknownUserError(ValueError):
    pass


def load_user_preferences(path: Path = PREFERENCES_PATH) -> dict[str, dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_memory_events(path: Path = EVENTS_PATH) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        events.append(json.loads(text))
    return events


def build_memory_snapshot(
    user_id: str,
    preferences_path: Path = PREFERENCES_PATH,
    events_path: Path = EVENTS_PATH,
) -> dict[str, Any]:
    profiles = load_user_preferences(preferences_path)
    if user_id not in profiles:
        raise UnknownUserError(f"Unknown mock user_id: {user_id}")

    events = [event for event in load_memory_events(events_path) if event.get("user_id") == user_id]
    return {
        "user_id": user_id,
        "base_profile": dict(profiles[user_id]),
        "events": events,
        "event_count": len(events),
        "source_files": [preferences_path.name, events_path.name],
        "privacy_note": "Local mock memory only; no real user identity or private account data.",
    }
