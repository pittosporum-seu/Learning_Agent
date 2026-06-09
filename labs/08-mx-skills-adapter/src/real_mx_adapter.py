from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping

from adapter_contract import AdapterResult, CANONICAL_CAPABILITIES, normalize_capability


EXTERNAL_PROVIDER_BLOCKED_REASON = "external provider requires explicit CLI confirmation and environment configuration"
DEFAULT_PROVIDER_PROFILE = "mx-skills"
MX_PROVIDER_DOWNLOAD_URL = "https://dl.dfcfs.com/m/itc4"
DEFAULT_MX_API_BASE_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw"
CAPABILITY_ENDPOINTS = {
    "candidate-screen": "stock-screen",
    "market-data": "query",
    "finance-news": "news-search",
}


Transport = Callable[[str, dict[str, str], dict[str, Any], int], dict[str, Any]]


def _env_flag_is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


class ExternalFinanceAdapter:
    adapter_name = "external-finance"
    provider_mode = "external"
    capabilities = CANONICAL_CAPABILITIES

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
        canonical_capability = normalize_capability(capability)
        if canonical_capability not in self.capabilities:
            return self._result(
                capability=canonical_capability,
                input_summary={"payload_keys": sorted(payload)},
                output={"disabled": True, "reason": f"Unsupported external capability: {capability}"},
                status="failed",
                error=f"Unsupported external capability: {capability}",
                network_request_sent=False,
                api_key_present=False,
            )

        gate = self.evaluate_gate()
        input_summary = summarize_payload(payload)
        input_summary["provider_profile"] = gate["provider_profile"]
        if not gate["allowed"]:
            return self._result(
                capability=canonical_capability,
                input_summary=input_summary,
                output={
                    "disabled": True,
                    "reason": EXTERNAL_PROVIDER_BLOCKED_REASON,
                    "missing_conditions": gate["missing_conditions"],
                    "provider_profile": gate["provider_profile"],
                    "provider_download_url": gate["provider_download_url"],
                    "network_request_sent": False,
                    "api_key_present": gate["api_key_present"],
                    "raw_response_persisted": False,
                },
                status="blocked",
                error=EXTERNAL_PROVIDER_BLOCKED_REASON,
                network_request_sent=False,
                api_key_present=gate["api_key_present"],
            )

        provider_secret = resolve_provider_api_key(self.env)
        base_url = gate["base_url"]
        timeout_seconds = resolve_provider_timeout_seconds(self.env)
        url = build_provider_url(base_url, canonical_capability, gate["provider_profile"])
        request_payload = build_provider_payload(canonical_capability, payload, gate["provider_profile"])
        headers = build_provider_headers(provider_secret, self.env, gate["provider_profile"])

        try:
            response = self.transport(url, headers, request_payload, timeout_seconds)
        except Exception as exc:  # pragma: no cover - exercised through fake transports in tests.
            return self._result(
                capability=canonical_capability,
                input_summary=input_summary,
                output={
                    "provider_status": "request_failed",
                    "provider_profile": gate["provider_profile"],
                    "error_type": exc.__class__.__name__,
                    "raw_response_persisted": False,
                },
                status="failed",
                error=str(exc),
                network_request_sent=True,
                api_key_present=True,
            )

        return self._result(
            capability=canonical_capability,
            input_summary=input_summary,
            output=summarize_provider_response(response, gate["provider_profile"]),
            status=response.get("status", "success"),
            error=response.get("error"),
            network_request_sent=True,
            api_key_present=True,
        )

    def evaluate_gate(self) -> dict[str, Any]:
        missing_conditions: list[str] = []
        provider_profile = resolve_provider_profile(self.env)
        env_allows_real = env_allows_external_provider(self.env)

        if not self.allow_real_provider:
            missing_conditions.append("--allow-real-provider")
        if not env_allows_real:
            missing_conditions.append("FINANCE_PROVIDER_ALLOW_REAL=true or MX_ALLOW_REAL_PROVIDER=true")

        should_read_key_presence = self.allow_real_provider and env_allows_real
        api_key_present = has_provider_api_key(self.env) if should_read_key_presence else False
        base_url = ""
        base_url_source = ""
        if should_read_key_presence:
            base_url, base_url_source = resolve_external_base_url(self.env, provider_profile)
            if not api_key_present:
                missing_conditions.append("FINANCE_PROVIDER_API_KEY or MX_APIKEY")

        return {
            "allowed": self.allow_real_provider and env_allows_real and api_key_present and bool(base_url),
            "missing_conditions": missing_conditions,
            "api_key_present": api_key_present,
            "base_url_present": bool(base_url),
            "base_url": base_url,
            "base_url_source": base_url_source,
            "provider_profile": provider_profile,
            "provider_download_url": MX_PROVIDER_DOWNLOAD_URL if provider_profile == "mx-skills" else "",
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


def resolve_provider_profile(env: Mapping[str, str]) -> str:
    return str(env.get("FINANCE_PROVIDER_PROFILE") or DEFAULT_PROVIDER_PROFILE).strip() or DEFAULT_PROVIDER_PROFILE


def env_allows_external_provider(env: Mapping[str, str]) -> bool:
    return _env_flag_is_true(env.get("FINANCE_PROVIDER_ALLOW_REAL")) or _env_flag_is_true(env.get("MX_ALLOW_REAL_PROVIDER"))


def has_provider_api_key(env: Mapping[str, str]) -> bool:
    return bool(resolve_provider_api_key(env))


def resolve_provider_api_key(env: Mapping[str, str]) -> str:
    return str(env.get("FINANCE_PROVIDER_API_KEY") or env.get("MX_APIKEY") or "")


def resolve_provider_timeout_seconds(env: Mapping[str, str]) -> int:
    raw_value = env.get("FINANCE_PROVIDER_TIMEOUT_SECONDS") or env.get("MX_TIMEOUT_SECONDS") or "10"
    try:
        return max(1, int(str(raw_value)))
    except ValueError:
        return 10


def resolve_external_base_url(env: Mapping[str, str], provider_profile: str | None = None) -> tuple[str, str]:
    for name in ("FINANCE_PROVIDER_BASE_URL", "MX_SKILLS_BASE_URL", "MX_BASE_URL", "MX_API_URL"):
        value = str(env.get(name) or "").strip()
        if value:
            return normalize_external_base_url(value, provider_profile or resolve_provider_profile(env)), name
    if (provider_profile or resolve_provider_profile(env)) == "mx-skills":
        return DEFAULT_MX_API_BASE_URL, "default_mx_api_base_url"
    return "", ""


def normalize_external_base_url(base_url: str, provider_profile: str) -> str:
    normalized = base_url.rstrip("/")
    if provider_profile == "mx-skills":
        for endpoint in CAPABILITY_ENDPOINTS.values():
            suffix = f"/{endpoint}"
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)]
                break
        if not normalized.endswith("/api/claw"):
            normalized = f"{normalized}/api/claw"
    return normalized


def build_provider_url(base_url: str, capability: str, provider_profile: str) -> str:
    if provider_profile == "mx-skills":
        return f"{base_url.rstrip('/')}/{CAPABILITY_ENDPOINTS[capability]}"
    return f"{base_url.rstrip('/')}/{capability}"


def build_provider_headers(api_key: str, env: Mapping[str, str], provider_profile: str) -> dict[str, str]:
    header_name = str(env.get("FINANCE_PROVIDER_API_KEY_HEADER") or "").strip()
    headers = {"Content-Type": "application/json"}
    if header_name:
        headers[header_name] = api_key
    elif provider_profile == "mx-skills":
        headers["apikey"] = api_key
    else:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def summarize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_ids = payload.get("candidate_ids") or []
    strategy_spec = payload.get("strategy_spec") or {}
    return {
        "payload_keys": sorted(payload),
        "candidate_id_count": len(candidate_ids) if isinstance(candidate_ids, list) else 0,
        "strategy_fields": sorted(strategy_spec) if isinstance(strategy_spec, dict) else [],
        "has_request_text": bool(payload.get("request")),
    }


def build_provider_payload(capability: str, payload: dict[str, Any], provider_profile: str = DEFAULT_PROVIDER_PROFILE) -> dict[str, Any]:
    query = extract_provider_query(payload)
    if provider_profile == "mx-skills":
        if capability == "candidate-screen":
            return {"keyword": query}
        if capability == "market-data":
            return {"toolQuery": query}
        return {"query": query}
    return {"capability": capability, "query": query}


def extract_provider_query(payload: dict[str, Any]) -> str:
    strategy_spec = payload.get("strategy_spec")
    if isinstance(payload.get("request"), str) and payload["request"].strip():
        return payload["request"].strip()
    if isinstance(strategy_spec, dict) and isinstance(strategy_spec.get("original_request"), str):
        return strategy_spec["original_request"].strip()
    candidate_ids = payload.get("candidate_ids")
    if isinstance(candidate_ids, list) and candidate_ids:
        return " ".join(str(item) for item in candidate_ids)
    return "Learning_Agent Lab 08 manual provider check"


def summarize_provider_response(response: dict[str, Any], provider_profile: str) -> dict[str, Any]:
    body = response.get("body")
    body_summary: dict[str, Any] = {"body_type": type(body).__name__}
    if isinstance(body, dict):
        body_summary["top_level_fields"] = sorted(body)[:20]
        body_summary["field_count"] = len(body)
    elif isinstance(body, list):
        body_summary["item_count"] = len(body)

    return {
        "provider_status": response.get("status", "success"),
        "provider_profile": provider_profile,
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


RealMXAdapter = ExternalFinanceAdapter
REAL_PROVIDER_BLOCKED_REASON = EXTERNAL_PROVIDER_BLOCKED_REASON
REAL_PROVIDER_CAPABILITIES = CANONICAL_CAPABILITIES
resolve_mx_base_url = resolve_external_base_url
normalize_mx_base_url = lambda base_url: normalize_external_base_url(base_url, DEFAULT_PROVIDER_PROFILE)
