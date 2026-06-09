from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from finance_tools import fetch_market_data, search_finance_news, select_candidates


ToolHandler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    provider: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    handler: ToolHandler


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "provider": tool.provider,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
            }
            for tool in self._tools.values()
        ]

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        tool = self.get(name)
        return tool.handler(**kwargs)


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="select_candidates",
            description="Filter mock candidate universe by StrategySpec themes and candidate rules.",
            provider="local-mock",
            input_schema={"strategy_spec": "dict", "max_candidates": "int|None"},
            output_schema={"candidates": "list", "rejected": "list", "input_summary": "dict"},
            handler=select_candidates,
        )
    )
    registry.register(
        ToolDefinition(
            name="fetch_market_data",
            description="Return mock trend, drawdown, turnover, and valuation evidence.",
            provider="local-mock",
            input_schema={"candidate_ids": "list[str]"},
            output_schema={"market_items": "list", "missing_candidate_ids": "list"},
            handler=fetch_market_data,
        )
    )
    registry.register(
        ToolDefinition(
            name="search_finance_news",
            description="Return mock news snippets and risk flags for candidates.",
            provider="local-mock",
            input_schema={"candidate_ids": "list[str]"},
            output_schema={"news_items": "list", "risk_flags": "list"},
            handler=search_finance_news,
        )
    )
    return registry
