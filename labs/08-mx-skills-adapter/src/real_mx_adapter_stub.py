from __future__ import annotations

from typing import Any

from adapter_contract import AdapterResult


REAL_PROVIDER_DISABLED_REASON = "real provider requires future explicit confirmation and environment key"


class RealMXAdapterStub:
    adapter_name = "real-mx-stub"
    provider_mode = "real_stub"
    capabilities = {"mx-xuangu", "mx-data", "mx-search"}

    def call(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        return AdapterResult(
            adapter_name=self.adapter_name,
            provider_mode=self.provider_mode,
            capability=capability,
            input_summary={"payload_keys": sorted(payload)},
            output={
                "disabled": True,
                "reason": REAL_PROVIDER_DISABLED_REASON,
                "network_request_sent": False,
                "api_key_read": False,
            },
            status="blocked",
            error=REAL_PROVIDER_DISABLED_REASON,
            requires_api_key=True,
            requires_human_confirmation=True,
        ).to_dict()
