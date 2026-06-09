from __future__ import annotations

from typing import Any


def build_candidate_evidence(
    candidates: list[dict[str, Any]],
    market_result: dict[str, Any],
    news_result: dict[str, Any],
) -> list[dict[str, Any]]:
    market_by_id = {item["candidate_id"]: item for item in market_result.get("market_items", [])}
    news_by_id: dict[str, list[dict[str, Any]]] = {}
    for item in news_result.get("news_items", []):
        news_by_id.setdefault(item["candidate_id"], []).append(item)

    evidence: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        market_item = market_by_id.get(candidate_id)
        news_items = news_by_id.get(candidate_id, [])
        risk_flags = sorted(
            {
                flag
                for item in news_items
                for flag in item.get("risk_flags", [])
                if flag != "none"
            }
        )
        evidence_items: list[dict[str, Any]] = [
            {
                "evidence_id": f"{candidate_id}-candidate",
                "source_type": "mock_universe",
                "source_name": candidate.get("mock_source", "mock_universe.csv"),
                "claim": "Candidate matched StrategySpec theme and screening rules.",
                "value": {
                    "matched_theme": candidate.get("matched_theme"),
                    "matched_rules": candidate.get("matched_rules", []),
                },
                "confidence": "mock",
                "limitations": "Local mock universe only; not real market coverage.",
            }
        ]

        if market_item:
            evidence_items.append(
                {
                    "evidence_id": f"{candidate_id}-market",
                    "source_type": "mock_market_data",
                    "source_name": market_item.get("mock_source", "mock_prices.csv"),
                    "claim": "Mock market data is available for trend and drawdown inspection.",
                    "value": {
                        "trend_score": market_item["trend_score"],
                        "max_drawdown": market_item["max_drawdown"],
                        "turnover_level": market_item["turnover_level"],
                        "valuation_note": market_item["valuation_note"],
                    },
                    "confidence": "mock",
                    "limitations": "Values are deterministic fixtures for Tool Use teaching.",
                }
            )

        for index, news_item in enumerate(news_items, start=1):
            evidence_items.append(
                {
                    "evidence_id": f"{candidate_id}-news-{index}",
                    "source_type": "mock_news",
                    "source_name": news_item.get("mock_source", "mock_news.md"),
                    "claim": news_item["title"],
                    "value": {
                        "date": news_item["date"],
                        "sentiment": news_item["sentiment"],
                        "summary": news_item["summary"],
                        "risk_flags": news_item.get("risk_flags", []),
                    },
                    "confidence": "mock",
                    "limitations": "News snippet is local mock text, not a real news item.",
                }
            )

        evidence.append(
            {
                "candidate_id": candidate_id,
                "candidate_name": candidate["candidate_name"],
                "theme": candidate["theme"],
                "market": candidate["market"],
                "risk_flags": risk_flags,
                "evidence_items": evidence_items,
            }
        )

    return evidence
