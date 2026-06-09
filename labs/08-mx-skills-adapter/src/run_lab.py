from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from adapter_registry import DEFAULT_ADAPTER_NAME, AdapterRegistry, build_default_registry


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


def run_mx_skills_adapter(
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
        "real_provider_attempted": adapter_mode == "real-mx",
        "real_provider_allowed": safety_gate["real_provider_allowed"],
        "final_output": {},
        "risk_disclosure": skill_generation_output.get("risk_disclosure", RISK_DISCLOSURE),
        "next_lab": "Lab 09 Research Planner DAG",
    }

    if output["status"] != "completed":
        output["final_output"] = build_final_output(output)
        assert_no_prohibited_output_keys(output)
        return output

    selected_capabilities = capabilities or ["mx-xuangu", "mx-data", "mx-search"]

    if adapter_mode == "real-mx-stub":
        output["adapter_trace"] = [
            registry.call_adapter(
                capability="mx-xuangu",
                payload={"request": request, "reason": "real provider stub safety gate check"},
                adapter_name=adapter_mode,
            )
        ]
        output["status"] = "blocked"
        output["final_output"] = build_final_output(output)
        assert_no_prohibited_output_keys(output)
        return output

    if adapter_mode == "real-mx":
        strategy_spec = extract_strategy_spec(skill_generation_output)
        if not safety_gate["real_provider_allowed"]:
            output["adapter_trace"] = [
                registry.call_adapter(
                    capability="mx-xuangu",
                    payload={"request": request, "strategy_spec": strategy_spec, "reason": "real provider safety gate check"},
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
    xuangu_result = registry.call_adapter("mx-xuangu", {"strategy_spec": strategy_spec}, adapter_name=adapter_mode)
    candidate_ids = [item["candidate_id"] for item in xuangu_result.get("output", {}).get("candidates", [])]
    data_result = registry.call_adapter("mx-data", {"candidate_ids": candidate_ids}, adapter_name=adapter_mode)
    search_result = registry.call_adapter("mx-search", {"candidate_ids": candidate_ids}, adapter_name=adapter_mode)
    output["adapter_trace"] = [xuangu_result, data_result, search_result]
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
    return getattr(registry.get_adapter(adapter_mode), "provider_mode", "unknown")


def build_safety_gate(adapter_mode: str, allow_real_provider: bool = False, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = env if env is not None else os.environ
    real_provider_attempted = adapter_mode == "real-mx"
    env_allows_real = str(env.get("MX_ALLOW_REAL_PROVIDER", "")).strip().lower() in {"1", "true", "yes", "on"}
    should_check_secret_presence = real_provider_attempted and allow_real_provider and env_allows_real
    api_key_present = bool(env.get("MX_APIKEY")) if should_check_secret_presence else False
    base_url_present = bool(env.get("MX_SKILLS_BASE_URL") or env.get("MX_BASE_URL")) if should_check_secret_presence else False
    missing_conditions: list[str] = []

    if real_provider_attempted:
        if not allow_real_provider:
            missing_conditions.append("--allow-real-provider")
        if not env_allows_real:
            missing_conditions.append("MX_ALLOW_REAL_PROVIDER=true")
        if should_check_secret_presence and not api_key_present:
            missing_conditions.append("MX_APIKEY")
        if should_check_secret_presence and not base_url_present:
            missing_conditions.append("MX_SKILLS_BASE_URL or MX_BASE_URL")

    real_provider_allowed = real_provider_attempted and allow_real_provider and env_allows_real and api_key_present and base_url_present
    return {
        "real_provider_allowed": real_provider_allowed,
        "real_provider_attempted": real_provider_attempted,
        "active_adapter_mode": adapter_mode,
        "default_adapter_mode": DEFAULT_ADAPTER_NAME,
        "reason": (
            "real provider allowed by explicit CLI flag and environment gate"
            if real_provider_allowed
            else "real provider requires explicit CLI confirmation and environment configuration"
        ),
        "missing_conditions": missing_conditions,
        "api_key_present": api_key_present,
        "base_url_present": base_url_present,
        "raw_response_persisted": False,
        "required_conditions_for_real_provider": [
            "adapter_mode=real-mx",
            "--allow-real-provider",
            "MX_ALLOW_REAL_PROVIDER=true",
            "environment-provided MX_APIKEY",
            "MX_SKILLS_BASE_URL or MX_BASE_URL",
            "no persistence of authenticated responses",
        ],
    }


def build_final_output(output: dict[str, Any]) -> dict[str, Any]:
    adapter_statuses = [event.get("status") for event in output.get("adapter_trace", [])]
    return {
        "summary": (
            "MX Skills Adapter completed with mock adapter only."
            if output["status"] == "completed"
            else "MX Skills Adapter stopped before normal adapter execution."
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Lab 08 MX Skills Adapter.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--user-id", default="conservative_user", help="Mock user id.")
    parser.add_argument("--adapter-mode", choices=["mock-mx", "real-mx", "real-mx-stub"], default=DEFAULT_ADAPTER_NAME, help="Adapter name; defaults to mock-mx.")
    parser.add_argument("--allow-real-provider", action="store_true", help="Allow the real provider path when environment gates also pass.")
    parser.add_argument("--capabilities", default="mx-xuangu,mx-data,mx-search", help="Comma-separated adapter capabilities to call.")
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
            run_mx_skills_adapter(
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
