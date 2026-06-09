from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AdapterCapability:
    adapter_name: str
    provider_mode: str
    capability: str
    description: str
    requires_api_key: bool
    requires_human_confirmation: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdapterResult:
    adapter_name: str
    provider_mode: str
    capability: str
    input_summary: dict[str, Any]
    output: dict[str, Any]
    status: str
    error: str | None
    requires_api_key: bool
    requires_human_confirmation: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ADAPTER_RESULT_FIELDS = [
    "adapter_name",
    "provider_mode",
    "capability",
    "input_summary",
    "output",
    "status",
    "error",
    "requires_api_key",
    "requires_human_confirmation",
]


def validate_adapter_result(result: dict[str, Any]) -> bool:
    return all(field in result for field in ADAPTER_RESULT_FIELDS)
