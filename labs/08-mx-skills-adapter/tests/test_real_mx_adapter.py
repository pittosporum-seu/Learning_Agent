from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from real_mx_adapter import ExternalFinanceAdapter  # noqa: E402


class ExternalFinanceAdapterTest(unittest.TestCase):
    def test_real_adapter_missing_key_is_blocked_without_network(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
            calls.append({"url": url, "headers": headers, "payload": payload, "timeout_seconds": timeout_seconds})
            return {"status": "success", "http_status": 200, "body": {"ok": True}, "error": None}

        adapter = ExternalFinanceAdapter(
            allow_real_provider=True,
            env={"FINANCE_PROVIDER_ALLOW_REAL": "true", "FINANCE_PROVIDER_BASE_URL": "https://example.invalid/mx"},
            transport=fake_transport,
        )
        result = adapter.call("market-data", {"candidate_ids": ["MOCK_GRID_001"]})

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["network_request_sent"])
        self.assertFalse(result["api_key_present"])
        self.assertEqual(calls, [])

    def test_real_adapter_missing_cli_allow_is_blocked_without_reading_key(self) -> None:
        adapter = ExternalFinanceAdapter(
            allow_real_provider=False,
            env={
                "FINANCE_PROVIDER_ALLOW_REAL": "true",
                "FINANCE_PROVIDER_API_KEY": "fake-key",
                "FINANCE_PROVIDER_BASE_URL": "https://example.invalid/mx",
            },
        )
        result = adapter.call("finance-news", {"candidate_ids": ["MOCK_GRID_001"]})

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["network_request_sent"])
        self.assertFalse(result["api_key_present"])
        self.assertIn("--allow-real-provider", result["output"]["missing_conditions"])

    def test_real_adapter_success_path_uses_fake_transport(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
            calls.append({"url": url, "headers": headers, "payload": payload, "timeout_seconds": timeout_seconds})
            return {
                "status": "success",
                "http_status": 200,
                "body": {"items": [{"id": "MOCK_GRID_001"}], "source": "fake_transport"},
                "error": None,
            }

        adapter = ExternalFinanceAdapter(
            allow_real_provider=True,
            env={
                "FINANCE_PROVIDER_ALLOW_REAL": "true",
                "FINANCE_PROVIDER_API_KEY": "fake-key",
                "FINANCE_PROVIDER_BASE_URL": "https://example.invalid/mx",
                "FINANCE_PROVIDER_TIMEOUT_SECONDS": "3",
            },
            transport=fake_transport,
        )
        result = adapter.call("candidate-screen", {"request": "mock request", "strategy_spec": {"themes": ["grid"]}})

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["network_request_sent"])
        self.assertTrue(result["api_key_present"])
        self.assertFalse(result["raw_response_persisted"])
        self.assertEqual(len(calls), 1)
        self.assertNotIn("fake-key", str(result))
        self.assertNotIn("raw", result["output"])

    def test_real_adapter_uses_default_endpoint_when_base_url_is_not_set(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
            calls.append({"url": url, "headers": headers, "payload": payload, "timeout_seconds": timeout_seconds})
            return {"status": "success", "http_status": 200, "body": {"ok": True}, "error": None}

        adapter = ExternalFinanceAdapter(
            allow_real_provider=True,
            env={
                "FINANCE_PROVIDER_ALLOW_REAL": "true",
                "FINANCE_PROVIDER_API_KEY": "fake-key",
            },
            transport=fake_transport,
        )
        result = adapter.call("finance-news", {"request": "mock default endpoint query"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["url"], "https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search")
        self.assertEqual(calls[0]["payload"], {"query": "mock default endpoint query"})
        self.assertIn("apikey", calls[0]["headers"])
        self.assertFalse(result["raw_response_persisted"])

    def test_real_adapter_accepts_legacy_mx_aliases(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
            calls.append({"url": url, "headers": headers, "payload": payload, "timeout_seconds": timeout_seconds})
            return {"status": "success", "http_status": 200, "body": {"ok": True}, "error": None}

        adapter = ExternalFinanceAdapter(
            allow_real_provider=True,
            env={
                "MX_ALLOW_REAL_PROVIDER": "true",
                "MX_APIKEY": "fake-key",
            },
            transport=fake_transport,
        )
        result = adapter.call("mx-data", {"request": "mock market data query"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["capability"], "market-data")
        self.assertEqual(calls[0]["payload"], {"toolQuery": "mock market data query"})


if __name__ == "__main__":
    unittest.main()
