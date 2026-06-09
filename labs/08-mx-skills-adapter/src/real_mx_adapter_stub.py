from __future__ import annotations

from typing import Any

from adapter_contract import AdapterResult, CANONICAL_CAPABILITIES, normalize_capability


EXTERNAL_PROVIDER_DISABLED_REASON = "external provider requires future explicit confirmation and environment key"


class ExternalFinanceAdapterStub:
    adapter_name = "external-finance-stub"
    provider_mode = "external_stub"
    capabilities = CANONICAL_CAPABILITIES

    def call(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        return AdapterResult(
            adapter_name=self.adapter_name,
            provider_mode=self.provider_mode,
            capability=normalize_capability(capability),
            input_summary={"payload_keys": sorted(payload)},
            output={
                "disabled": True,
                "reason": EXTERNAL_PROVIDER_DISABLED_REASON,
                "network_request_sent": False,
                "api_key_read": False,
            },
            status="blocked",
            error=EXTERNAL_PROVIDER_DISABLED_REASON,
            requires_api_key=True,
            requires_human_confirmation=True,
        ).to_dict()


RealMXAdapterStub = ExternalFinanceAdapterStub
REAL_PROVIDER_DISABLED_REASON = EXTERNAL_PROVIDER_DISABLED_REASON
