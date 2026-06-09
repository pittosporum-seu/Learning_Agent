from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import DEFAULT_REQUEST, run_finance_provider_adapter  # noqa: E402


def has_real_finance_environment() -> bool:
    return (
        (os.environ.get("RUN_REAL_FINANCE_INTEGRATION") == "1" or os.environ.get("RUN_REAL_MX_INTEGRATION") == "1")
        and (
            os.environ.get("FINANCE_PROVIDER_ALLOW_REAL", "").lower() == "true"
            or os.environ.get("MX_ALLOW_REAL_PROVIDER", "").lower() == "true"
        )
        and bool(os.environ.get("FINANCE_PROVIDER_API_KEY") or os.environ.get("MX_APIKEY"))
    )


@unittest.skipUnless(has_real_finance_environment(), "Real finance provider integration requires explicit local environment gates.")
class ManualRealFinanceAdapterIntegrationTest(unittest.TestCase):
    def test_manual_real_provider_result_has_safe_shape(self) -> None:
        result = run_finance_provider_adapter(
            request=DEFAULT_REQUEST,
            user_id="balanced_user",
            adapter_mode="external-finance",
            allow_real_provider=True,
            capabilities=["candidate-screen"],
        )

        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["real_provider_attempted"])
        self.assertTrue(result["safety_gate"]["api_key_present"])
        self.assertFalse(result["safety_gate"]["raw_response_persisted"])
        self.assertIn("risk_disclosure", result)
        self.assertGreaterEqual(len(result["adapter_trace"]), 1)
        self.assertTrue(result["adapter_trace"][0]["network_request_sent"])
        self.assertFalse(result["adapter_trace"][0]["raw_response_persisted"])


if __name__ == "__main__":
    unittest.main()
