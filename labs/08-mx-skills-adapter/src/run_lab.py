from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from adapter_contract import normalize_adapter_name, normalize_capability
from adapter_registry import DEFAULT_ADAPTER_NAME, AdapterRegistry, build_default_registry
from real_mx_adapter import (
    MX_PROVIDER_DOWNLOAD_URL,
    env_allows_external_provider,
    has_provider_api_key,
    resolve_external_base_url,
    resolve_provider_profile,
)


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB07_RUN_LAB = REPO_ROOT / "labs" / "07-skill-generation" / "src" / "run_lab.py"
PROHIBITED_OUTPUT_KEYS = {"buy", "sell", "recommendation", "target_price"}


def load_lab07_module() -> Any:
    lab07_src = LAB07_RUN_LAB.parent
    if str(lab07_src) not in sys.path:
        sys.path.insert(0, str(lab07_src))
    spec = importlib.util.spec_from_file_location("lab07_skill_generation_run_lab", LAB07_RUN_LAB)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 07 runner from {LAB07_RUN_LAB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LAB07 = load_lab07_module()
DEFAULT_REQUEST = _LAB07.DEFAULT_REQUEST
RISK_DISCLOSURE = _LAB07.RISK_DISCLOSURE
run_skill_generation = _LAB07.run_skill_generation


def run_finance_provider_adapter(
    request: str = DEFAULT_REQUEST,
    user_id: str = "conservative_user",
    adapter_mode: str = DEFAULT_ADAPTER_NAME,
    allow_real_provider: bool = False,
    capabilities: list[str] | None = None,
    registry: AdapterRegistry | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = env if env is not None else os.environ
    registry = registry or build_default_registry(allow_real_provider=allow_real_provider, env=env)
    adapter_mode = normalize_adapter_name(adapter_mode)
    skill_generation_output = run_skill_generation(request=request, user_id=user_id)
    provider_mode = get_provider_mode(registry, adapter_mode)
    safety_gate = build_safety_gate(adapter_mode, allow_real_provider=allow_real_provider, env=env)
    output: dict[str, Any] = {
        "request": request,
        "user_id": user_id,
        "status": "completed" if skill_generation_output.get("status") == "completed" else "blocked",
        "skill_generation_output": skill_generation_output,
        "registered_adapters": registry.list_adapters(),
        "adapter_mode": adapter_mode,
        "provider_mode": provider_mode,
        "adapter_trace": [],
        "safety_gate": safety_gate,
        "real_provider_attempted": adapter_mode == "external-finance",
        "real_provider_allowed": safety_gate["real_provider_allowed"],
        "final_output": {},
        "risk_disclosure": skill_generation_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 09 Research Planner DAG",
    }

    if output["status"] != "completed":
        output["final_output"] = build_final_output(output)
        assert_no_prohibited_output_keys(output)
        return output

    selected_capabilities = [normalize_capability(item) for item in (capabilities or ["candidate-screen", "market-data", "finance-news"])]

    if adapter_mode == "external-finance-stub":
        output["adapter_trace"] = [
            registry.call_adapter(
                capability="candidate-screen",
                payload={"request": request, "reason": "external provider stub safety gate check"},
                adapter_name=adapter_mode,
            )
        ]
        output["status"] = "blocked"
        output["final_output"] = build_final_output(output)
        assert_no_prohibited_output_keys(output)
        return output

    if adapter_mode == "external-finance":
        strategy_spec = extract_strategy_spec(skill_generation_output)
        if not safety_gate["real_provider_allowed"]:
            output["adapter_trace"] = [
                registry.call_adapter(
                    capability="candidate-screen",
                    payload={"request": request, "strategy_spec": strategy_spec, "reason": "external provider safety gate check"},
                    adapter_name=adapter_mode,
                )
            ]
            output["status"] = "blocked"
            output["final_output"] = build_final_output(output)
            assert_no_prohibited_output_keys(output)
            return output

        trace: list[dict[str, Any]] = []
        for capability in selected_capabilities:
            trace.append(
                registry.call_adapter(
                    capability=capability,
                    payload={"request": request, "strategy_spec": strategy_spec, "candidate_ids": []},
                    adapter_name=adapter_mode,
                )
            )
        output["adapter_trace"] = trace
        output["status"] = "completed"
        output["final_output"] = build_final_output(output)
        assert_no_prohibited_output_keys(output)
        return output

    if adapter_mode != DEFAULT_ADAPTER_NAME:
        raise KeyError(f"Unknown adapter mode: {adapter_mode}")

    strategy_spec = extract_strategy_spec(skill_generation_output)
    candidate_result = registry.call_adapter("candidate-screen", {"strategy_spec": strategy_spec}, adapter_name=adapter_mode)
    candidate_ids = [item["candidate_id"] for item in candidate_result.get("output", {}).get("candidates", [])]
    data_result = registry.call_adapter("market-data", {"candidate_ids": candidate_ids}, adapter_name=adapter_mode)
    search_result = registry.call_adapter("finance-news", {"candidate_ids": candidate_ids}, adapter_name=adapter_mode)
    output["adapter_trace"] = [candidate_result, data_result, search_result]
    output["final_output"] = build_final_output(output)
    assert_no_prohibited_output_keys(output)
    return output


def extract_strategy_spec(skill_generation_output: dict[str, Any]) -> dict[str, Any]:
    return (
        skill_generation_output.get("skill_registry_output", {})
        .get("memory_output", {})
        .get("rag_output", {})
        .get("strategy_spec", {})
    )


def get_provider_mode(registry: AdapterRegistry, adapter_mode: str) -> str:
    return getattr(registry.get_adapter(normalize_adapter_name(adapter_mode)), "provider_mode", "unknown")


def build_safety_gate(adapter_mode: str, allow_real_provider: bool = False, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = env if env is not None else os.environ
    adapter_mode = normalize_adapter_name(adapter_mode)
    real_provider_attempted = adapter_mode == "external-finance"
    provider_profile = resolve_provider_profile(env)
    env_allows_real = env_allows_external_provider(env)
    should_check_secret_presence = real_provider_attempted and allow_real_provider and env_allows_real
    api_key_present = has_provider_api_key(env) if should_check_secret_presence else False
    base_url = ""
    base_url_source = ""
    base_url_present = False
    if should_check_secret_presence:
        base_url, base_url_source = resolve_external_base_url(env, provider_profile)
        base_url_present = bool(base_url)
    missing_conditions: list[str] = []

    if real_provider_attempted:
        if not allow_real_provider:
            missing_conditions.append("--allow-real-provider")
        if not env_allows_real:
            missing_conditions.append("FINANCE_PROVIDER_ALLOW_REAL=true or MX_ALLOW_REAL_PROVIDER=true")
        if should_check_secret_presence and not api_key_present:
            missing_conditions.append("FINANCE_PROVIDER_API_KEY or MX_APIKEY")

    real_provider_allowed = real_provider_attempted and allow_real_provider and env_allows_real and api_key_present and base_url_present
    return {
        "real_provider_allowed": real_provider_allowed,
        "real_provider_attempted": real_provider_attempted,
        "active_adapter_mode": adapter_mode,
        "default_adapter_mode": DEFAULT_ADAPTER_NAME,
        "provider_profile": provider_profile,
        "provider_download_url": MX_PROVIDER_DOWNLOAD_URL if provider_profile == "mx-skills" else "",
        "reason": (
            "external provider allowed by explicit CLI flag and environment gate"
            if real_provider_allowed
            else "external provider requires explicit CLI confirmation and environment configuration"
        ),
        "missing_conditions": missing_conditions,
        "api_key_present": api_key_present,
        "base_url_present": base_url_present,
        "base_url_source": base_url_source,
        "raw_response_persisted": False,
        "required_conditions_for_real_provider": [
            "adapter_mode=external-finance",
            "--allow-real-provider",
            "FINANCE_PROVIDER_ALLOW_REAL=true or MX_ALLOW_REAL_PROVIDER=true",
            "environment-provided FINANCE_PROVIDER_API_KEY or MX_APIKEY",
            "optional FINANCE_PROVIDER_BASE_URL, MX_SKILLS_BASE_URL, MX_BASE_URL, or MX_API_URL; mx-skills otherwise uses the default public MX API endpoint",
            "no persistence of authenticated responses",
        ],
    }


def build_final_output(output: dict[str, Any]) -> dict[str, Any]:
    adapter_statuses = [event.get("status") for event in output.get("adapter_trace", [])]
    return {
        "summary": (
            "Finance Provider Adapter completed with mock adapter only."
            if output["status"] == "completed"
            else "Finance Provider Adapter stopped before normal adapter execution."
        ),
        "adapter_mode": output["adapter_mode"],
        "adapter_call_count": len(output.get("adapter_trace", [])),
        "adapter_statuses": adapter_statuses,
        "provider_mode": output["provider_mode"],
        "real_provider_attempted": output["real_provider_attempted"],
        "real_provider_allowed": output["safety_gate"]["real_provider_allowed"],
        "next_lab": output["next_lab"],
        "risk_disclosure": output["risk_disclosure"],
    }


def assert_no_prohibited_output_keys(value: Any) -> None:
    if isinstance(value, dict):
        overlap = PROHIBITED_OUTPUT_KEYS.intersection(value)
        if overlap:
            raise AssertionError(f"Prohibited output keys found: {sorted(overlap)}")
        for child in value.values():
            assert_no_prohibited_output_keys(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_prohibited_output_keys(child)


def run_mx_skills_adapter(
    request: str = DEFAULT_REQUEST,
    user_id: str = "conservative_user",
    adapter_mode: str = DEFAULT_ADAPTER_NAME,
    allow_real_provider: bool = False,
    capabilities: list[str] | None = None,
    registry: AdapterRegistry | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    return run_finance_provider_adapter(
        request=request,
        user_id=user_id,
        adapter_mode=adapter_mode,
        allow_real_provider=allow_real_provider,
        capabilities=capabilities,
        registry=registry,
        env=env,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Lab 08 Finance Provider Adapter.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument(
        "--adapter-mode",
        choices=["mock-finance", "external-finance", "external-finance-stub", "mock-mx", "real-mx", "real-mx-stub"],
        default=DEFAULT_ADAPTER_NAME,
        help="Adapter name; defaults to mock-finance. Legacy mx names are accepted as aliases.",
    )
    parser.add_argument("--allow-real-provider", action="store_true", help="Allow the external provider path when environment gates also pass.")
    parser.add_argument("--capabilities", default="candidate-screen,market-data,finance-news", help="Comma-separated adapter capabilities to call.")
    parser.add_argument("--input-file", help="Read request text from a UTF-8 file.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    if args.input_file:
        request = Path(args.input_file).read_text(encoding="utf-8")
    elif args.request:
        request = " ".join(args.request)
    else:
        request = DEFAULT_REQUEST

    print(
        json.dumps(
            run_finance_provider_adapter(
                request=request,
                user_id=args.user_id,
                adapter_mode=args.adapter_mode,
                allow_real_provider=args.allow_real_provider,
                capabilities=[item.strip() for item in args.capabilities.split(",") if item.strip()],
            ),
            ensure_ascii=False,
            indent=args.indent,
        )
    )


if __name__ == "__main__":
    main()
