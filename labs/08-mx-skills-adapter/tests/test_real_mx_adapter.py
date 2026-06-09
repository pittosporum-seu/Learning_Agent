from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from real_mx_adapter import RealMXAdapter  # noqa: E402


class RealMXAdapterTest(unittest.TestCase):
    def test_real_adapter_missing_key_is_blocked_without_network(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
            calls.append({"url": url, "headers": headers, "payload": payload, "timeout_seconds": timeout_seconds})
            return {"status": "success", "http_status": 200, "body": {"ok": True}, "error": None}

        adapter = RealMXAdapter(
            allow_real_provider=True,
            env={"MX_ALLOW_REAL_PROVIDER": "true", "MX_SKILLS_BASE_URL": "https://example.invalid/mx"},
            transport=fake_transport,
        )
        result = adapter.call("mx-data", {"candidate_ids": ["MOCK_GRID_001"]})

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["network_request_sent"])
        self.assertFalse(result["api_key_present"])
        self.assertEqual(calls, [])

    def test_real_adapter_missing_cli_allow_is_blocked_without_reading_key(self) -> None:
        adapter = RealMXAdapter(
            allow_real_provider=False,
            env={
                "MX_ALLOW_REAL_PROVIDER": "true",
                "MX_APIKEY": "fake-key",
                "MX_SKILLS_BASE_URL": "https://example.invalid/mx",
            },
        )
        result = adapter.call("mx-search", {"candidate_ids": ["MOCK_GRID_001"]})

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

        adapter = RealMXAdapter(
            allow_real_provider=True,
            env={
                "MX_ALLOW_REAL_PROVIDER": "true",
                "MX_APIKEY": "fake-key",
                "MX_SKILLS_BASE_URL": "https://example.invalid/mx",
                "MX_TIMEOUT_SECONDS": "3",
            },
            transport=fake_transport,
        )
        result = adapter.call("mx-xuangu", {"request": "mock request", "strategy_spec": {"themes": ["grid"]}})

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["network_request_sent"])
        self.assertTrue(result["api_key_present"])
        self.assertFalse(result["raw_response_persisted"])
        self.assertEqual(len(calls), 1)
        self.assertNotIn("fake-key", str(result))
        self.assertNotIn("raw", result["output"])


if __name__ == "__main__":
    unittest.main()
