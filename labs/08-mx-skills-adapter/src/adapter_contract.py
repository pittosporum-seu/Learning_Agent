from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


CANONICAL_CAPABILITIES = {"candidate-screen", "market-data", "finance-news"}

CAPABILITY_ALIASES = {
    "mx-xuangu": "candidate-screen",
    "mx-data": "market-data",
    "mx-search": "finance-news",
}

CANONICAL_ADAPTER_NAMES = {"mock-finance", "external-finance-stub", "external-finance"}

ADAPTER_ALIASES = {
    "mock-mx": "mock-finance",
    "real-mx-stub": "external-finance-stub",
    "real-mx": "external-finance",
}


def normalize_capability(capability: str) -> str:
    return CAPABILITY_ALIASES.get(capability, capability)


def normalize_adapter_name(adapter_name: str) -> str:
    return ADAPTER_ALIASES.get(adapter_name, adapter_name)


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
    network_request_sent: bool = False
    api_key_present: bool = False
    raw_response_persisted: bool = False

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
    "network_request_sent",
    "api_key_present",
    "raw_response_persisted",
]


def validate_adapter_result(result: dict[str, Any]) -> bool:
    return all(field in result for field in ADAPTER_RESULT_FIELDS)
