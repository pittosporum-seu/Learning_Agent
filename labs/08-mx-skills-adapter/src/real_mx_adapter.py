from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping

from adapter_contract import AdapterResult


REAL_PROVIDER_BLOCKED_REASON = "real provider requires explicit CLI confirmation and environment configuration"
REAL_PROVIDER_CAPABILITIES = {"mx-xuangu", "mx-data", "mx-search"}


Transport = Callable[[str, dict[str, str], dict[str, Any], int], dict[str, Any]]


def _env_flag_is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


class RealMXAdapter:
    adapter_name = "real-mx"
    provider_mode = "real"
    capabilities = REAL_PROVIDER_CAPABILITIES

    def __init__(
        self,
        allow_real_provider: bool = False,
        env: Mapping[str, str] | None = None,
        transport: Transport | None = None,
    ) -> None:
        self.allow_real_provider = allow_real_provider
        self.env = env if env is not None else os.environ
        self.transport = transport or default_transport

    def call(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        if capability not in self.capabilities:
            return self._result(
                capability=capability,
                input_summary={"payload_keys": sorted(payload)},
                output={"disabled": True, "reason": f"Unsupported real capability: {capability}"},
                status="failed",
                error=f"Unsupported real capability: {capability}",
                network_request_sent=False,
                api_key_present=False,
            )

        gate = self.evaluate_gate()
        input_summary = summarize_payload(payload)
        if not gate["allowed"]:
            return self._result(
                capability=capability,
                input_summary=input_summary,
                output={
                    "disabled": True,
                    "reason": REAL_PROVIDER_BLOCKED_REASON,
                    "missing_conditions": gate["missing_conditions"],
                    "network_request_sent": False,
                    "api_key_present": gate["api_key_present"],
                    "raw_response_persisted": False,
                },
                status="blocked",
                error=REAL_PROVIDER_BLOCKED_REASON,
                network_request_sent=False,
                api_key_present=gate["api_key_present"],
            )

        api_key = self.env["MX_APIKEY"]
        base_url = gate["base_url"]
        timeout_seconds = int(self.env.get("MX_TIMEOUT_SECONDS", "10") or "10")
        url = f"{base_url.rstrip('/')}/{capability}"
        request_payload = {"capability": capability, "input": payload}
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self.transport(url, headers, request_payload, timeout_seconds)
        except Exception as exc:  # pragma: no cover - exercised through fake transports in tests.
            return self._result(
                capability=capability,
                input_summary=input_summary,
                output={
                    "provider_status": "request_failed",
                    "error_type": exc.__class__.__name__,
                    "raw_response_persisted": False,
                },
                status="failed",
                error=str(exc),
                network_request_sent=True,
                api_key_present=True,
            )

        return self._result(
            capability=capability,
            input_summary=input_summary,
            output=summarize_provider_response(response),
            status=response.get("status", "success"),
            error=response.get("error"),
            network_request_sent=True,
            api_key_present=True,
        )

    def evaluate_gate(self) -> dict[str, Any]:
        missing_conditions: list[str] = []
        env_allows_real = _env_flag_is_true(self.env.get("MX_ALLOW_REAL_PROVIDER"))

        if not self.allow_real_provider:
            missing_conditions.append("--allow-real-provider")
        if not env_allows_real:
            missing_conditions.append("MX_ALLOW_REAL_PROVIDER=true")

        should_read_key_presence = self.allow_real_provider and env_allows_real
        api_key_present = bool(self.env.get("MX_APIKEY")) if should_read_key_presence else False
        base_url = ""
        if should_read_key_presence:
            base_url = self.env.get("MX_SKILLS_BASE_URL") or self.env.get("MX_BASE_URL") or ""
            if not api_key_present:
                missing_conditions.append("MX_APIKEY")
            if not base_url:
                missing_conditions.append("MX_SKILLS_BASE_URL or MX_BASE_URL")

        return {
            "allowed": self.allow_real_provider and env_allows_real and api_key_present and bool(base_url),
            "missing_conditions": missing_conditions,
            "api_key_present": api_key_present,
            "base_url_present": bool(base_url),
            "base_url": base_url,
        }

    def _result(
        self,
        capability: str,
        input_summary: dict[str, Any],
        output: dict[str, Any],
        status: str,
        error: str | None,
        network_request_sent: bool,
        api_key_present: bool,
    ) -> dict[str, Any]:
        return AdapterResult(
            adapter_name=self.adapter_name,
            provider_mode=self.provider_mode,
            capability=capability,
            input_summary=input_summary,
            output=output,
            status=status,
            error=error,
            requires_api_key=True,
            requires_human_confirmation=True,
            network_request_sent=network_request_sent,
            api_key_present=api_key_present,
            raw_response_persisted=False,
        ).to_dict()


def summarize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_ids = payload.get("candidate_ids") or []
    strategy_spec = payload.get("strategy_spec") or {}
    return {
        "payload_keys": sorted(payload),
        "candidate_id_count": len(candidate_ids) if isinstance(candidate_ids, list) else 0,
        "strategy_fields": sorted(strategy_spec) if isinstance(strategy_spec, dict) else [],
        "has_request_text": bool(payload.get("request")),
    }


def summarize_provider_response(response: dict[str, Any]) -> dict[str, Any]:
    body = response.get("body")
    body_summary: dict[str, Any] = {"body_type": type(body).__name__}
    if isinstance(body, dict):
        body_summary["top_level_fields"] = sorted(body)[:20]
        body_summary["field_count"] = len(body)
    elif isinstance(body, list):
        body_summary["item_count"] = len(body)

    return {
        "provider_status": response.get("status", "success"),
        "http_status": response.get("http_status"),
        "body_summary": body_summary,
        "raw_response_persisted": False,
    }


def default_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            try:
                body: Any = json.loads(raw_body)
            except json.JSONDecodeError:
                body = {"text_length": len(raw_body)}
            return {"status": "success", "http_status": response.status, "body": body, "error": None}
    except urllib.error.HTTPError as exc:
        return {
            "status": "provider_error",
            "http_status": exc.code,
            "body": {"error_type": "HTTPError"},
            "error": f"HTTP {exc.code}",
        }
