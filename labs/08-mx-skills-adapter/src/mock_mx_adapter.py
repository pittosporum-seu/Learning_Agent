from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from adapter_contract import AdapterResult, CANONICAL_CAPABILITIES, normalize_capability


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
LAB03_SRC = REPO_ROOT / "labs" / "03-finance-tool-use-mock" / "src"
LAB03_FINANCE_TOOLS = LAB03_SRC / "finance_tools.py"


def load_lab03_finance_tools() -> Any:
    if str(LAB03_SRC) not in sys.path:
        sys.path.insert(0, str(LAB03_SRC))
    spec = importlib.util.spec_from_file_location("lab03_finance_tools_for_mx_adapter", LAB03_FINANCE_TOOLS)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Lab 03 finance tools from {LAB03_FINANCE_TOOLS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_FINANCE_TOOLS = load_lab03_finance_tools()


class MockFinanceAdapter:
    adapter_name = "mock-finance"
    provider_mode = "mock"
    capabilities = CANONICAL_CAPABILITIES

    def call(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        canonical_capability = normalize_capability(capability)
        if canonical_capability not in self.capabilities:
            return self._result(
                capability=canonical_capability,
                input_summary={"payload_keys": sorted(payload)},
                output={},
                status="failed",
                error=f"Unsupported mock capability: {capability}",
            )

        if canonical_capability == "candidate-screen":
            strategy_spec = payload.get("strategy_spec") or {}
            result = _FINANCE_TOOLS.select_candidates(strategy_spec)
            return self._result(
                capability=canonical_capability,
                input_summary=result.get("input_summary", {}),
                output={"candidates": result.get("candidates", []), "rejected_count": len(result.get("rejected", []))},
                status="success",
                error=None,
            )

        candidate_ids = list(payload.get("candidate_ids") or [])
        if canonical_capability == "market-data":
            result = _FINANCE_TOOLS.fetch_market_data(candidate_ids)
            return self._result(
                capability=canonical_capability,
                input_summary={"candidate_ids": candidate_ids},
                output=result,
                status="success",
                error=None,
            )

        result = _FINANCE_TOOLS.search_finance_news(candidate_ids)
        return self._result(
            capability=canonical_capability,
            input_summary={"candidate_ids": candidate_ids},
            output=result,
            status="success",
            error=None,
        )

    def _result(
        self,
        capability: str,
        input_summary: dict[str, Any],
        output: dict[str, Any],
        status: str,
        error: str | None,
    ) -> dict[str, Any]:
        return AdapterResult(
            adapter_name=self.adapter_name,
            provider_mode=self.provider_mode,
            capability=capability,
            input_summary=input_summary,
            output=output,
            status=status,
            error=error,
            requires_api_key=False,
            requires_human_confirmation=False,
        ).to_dict()


MockMXAdapter = MockFinanceAdapter
