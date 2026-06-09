from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from adapter_contract import AdapterCapability
from mock_mx_adapter import MockMXAdapter
from real_mx_adapter import RealMXAdapter
from real_mx_adapter_stub import RealMXAdapterStub


LAB_ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_PATH = LAB_ROOT / "data" / "adapter_capabilities.json"
DEFAULT_ADAPTER_NAME = "mock-mx"


class AdapterRegistry:
    def __init__(self, adapters: dict[str, Any], capabilities: list[dict[str, Any]]) -> None:
        self._adapters = adapters
        self._capability_docs = capabilities

    @classmethod
    def build_default(cls, allow_real_provider: bool = False, env: Mapping[str, str] | None = None) -> "AdapterRegistry":
        capabilities = json.loads(CAPABILITIES_PATH.read_text(encoding="utf-8"))
        adapters = {
            "mock-mx": MockMXAdapter(),
            "real-mx-stub": RealMXAdapterStub(),
            "real-mx": RealMXAdapter(allow_real_provider=allow_real_provider, env=env),
        }
        return cls(adapters=adapters, capabilities=capabilities)

    def list_adapters(self) -> list[dict[str, Any]]:
        return self._capability_docs

    def list_capabilities(self) -> list[dict[str, Any]]:
        docs: list[dict[str, Any]] = []
        for adapter in self._capability_docs:
            for capability in adapter.get("capabilities", []):
                docs.append(
                    AdapterCapability(
                        adapter_name=adapter["adapter_name"],
                        provider_mode=adapter["provider_mode"],
                        capability=capability["name"],
                        description=capability["description"],
                        requires_api_key=bool(capability["requires_api_key"]),
                        requires_human_confirmation=bool(capability["requires_human_confirmation"]),
                    ).to_dict()
                )
        return docs

    def get_adapter(self, adapter_name: str = DEFAULT_ADAPTER_NAME) -> Any:
        try:
            return self._adapters[adapter_name]
        except KeyError as exc:
            raise KeyError(f"Unknown adapter: {adapter_name}") from exc

    def call_adapter(self, capability: str, payload: dict[str, Any], adapter_name: str = DEFAULT_ADAPTER_NAME) -> dict[str, Any]:
        adapter = self.get_adapter(adapter_name)
        return adapter.call(capability=capability, payload=payload)


def build_default_registry(allow_real_provider: bool = False, env: Mapping[str, str] | None = None) -> AdapterRegistry:
    return AdapterRegistry.build_default(allow_real_provider=allow_real_provider, env=env)
