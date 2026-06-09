from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = LAB_ROOT / "data"
UNIVERSE_PATH = DATA_DIR / "mock_universe.csv"
PRICES_PATH = DATA_DIR / "mock_prices.csv"
NEWS_PATH = DATA_DIR / "mock_news.md"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def select_candidates(
    strategy_spec: dict[str, Any],
    data_path: Path = UNIVERSE_PATH,
    max_candidates: int | None = None,
) -> dict[str, Any]:
    themes = set(strategy_spec.get("themes") or [])
    candidate_rules = strategy_spec.get("candidate_rules") or []
    risk_filters = strategy_spec.get("risk_filters") or []
    profile = strategy_spec.get("user_preferences") or {}
    max_count = max_candidates or int(profile.get("max_candidates", 10))

    rows = read_csv_rows(data_path)
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for row in rows:
        reasons = explain_candidate_match(row, themes, candidate_rules, risk_filters)
        if reasons["matched"]:
            candidates.append(
                {
                    "candidate_id": row["candidate_id"],
                    "candidate_name": row["candidate_name"],
                    "market": row["market"],
                    "theme": row["theme"],
                    "matched_rules": reasons["matched_rules"],
                    "matched_theme": reasons["matched_theme"],
                    "mock_source": str(data_path.name),
                }
            )
        else:
            rejected.append(
                {
                    "candidate_id": row["candidate_id"],
                    "reason": reasons["reason"],
                }
            )

    return {
        "candidates": candidates[:max_count],
        "rejected": rejected,
        "input_summary": {
            "themes": sorted(themes),
            "candidate_rules": candidate_rules,
            "risk_filters": risk_filters,
            "max_candidates": max_count,
        },
    }


def explain_candidate_match(
    row: dict[str, str],
    themes: set[str],
    candidate_rules: list[str],
    risk_filters: list[str],
) -> dict[str, Any]:
    if themes and row["theme"] not in themes:
        return {"matched": False, "reason": "theme_not_matched", "matched_rules": [], "matched_theme": None}

    if row.get("negative_news", "").lower() == "true" and any("负面" in item for item in risk_filters):
        return {"matched": False, "reason": "negative_news_filtered", "matched_rules": [], "matched_theme": row["theme"]}

    matched_rules = [
        rule
        for rule in candidate_rules
        if rule_matches_row(rule, row)
    ]

    if candidate_rules and not matched_rules:
        return {"matched": False, "reason": "candidate_rules_not_matched", "matched_rules": [], "matched_theme": row["theme"]}

    return {
        "matched": True,
        "reason": "matched",
        "matched_rules": matched_rules or ["theme_match"],
        "matched_theme": row["theme"],
    }


def rule_matches_row(rule: str, row: dict[str, str]) -> bool:
    tags = row.get("tags", "")
    if "趋势" in rule:
        return row.get("trend_label") in {"strong", "very_strong"} or "趋势较强" in tags
    if "回撤" in rule:
        return row.get("drawdown_label") in {"low", "medium_low"} or "回撤较低" in tags
    if "成交" in rule or "流动" in rule:
        return row.get("liquidity_level") in {"medium", "high"} or "成交活跃" in tags
    if "市盈率" in rule:
        return "市盈率小于20" in tags
    if "ROE" in rule:
        return "ROE" in tags
    return rule in tags


def fetch_market_data(
    candidate_ids: list[str],
    data_path: Path = PRICES_PATH,
) -> dict[str, Any]:
    rows = {row["candidate_id"]: row for row in read_csv_rows(data_path)}
    market_items: list[dict[str, Any]] = []
    missing: list[str] = []

    for candidate_id in candidate_ids:
        row = rows.get(candidate_id)
        if row is None:
            missing.append(candidate_id)
            continue
        market_items.append(
            {
                "candidate_id": candidate_id,
                "trend_score": float(row["trend_score"]),
                "max_drawdown": float(row["max_drawdown"]),
                "turnover_level": row["turnover_level"],
                "valuation_note": row["valuation_note"],
                "mock_source": str(data_path.name),
            }
        )

    return {
        "market_items": market_items,
        "missing_candidate_ids": missing,
    }


def search_finance_news(
    candidate_ids: list[str],
    data_path: Path = NEWS_PATH,
) -> dict[str, Any]:
    news_items = [
        item
        for item in parse_mock_news(data_path)
        if item["candidate_id"] in candidate_ids
    ]
    risk_flags = sorted(
        {
            flag
            for item in news_items
            for flag in item.get("risk_flags", [])
            if flag != "none"
        }
    )
    return {
        "news_items": news_items,
        "risk_flags": risk_flags,
    }


def parse_mock_news(path: Path = NEWS_PATH) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text.startswith("- candidate_id="):
            continue
        fields: dict[str, str] = {}
        for part in text[2:].split(" | "):
            key, _, value = part.partition("=")
            fields[key.strip()] = value.strip()
        risk_flags = [flag.strip() for flag in fields.get("risk_flags", "none").split(";") if flag.strip()]
        items.append(
            {
                "candidate_id": fields["candidate_id"],
                "date": fields["date"],
                "sentiment": fields["sentiment"],
                "risk_flags": risk_flags,
                "title": fields["title"],
                "summary": fields["summary"],
                "mock_source": str(path.name),
            }
        )
    return items
