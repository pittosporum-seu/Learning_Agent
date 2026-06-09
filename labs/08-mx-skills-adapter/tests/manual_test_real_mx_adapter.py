from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_lab import DEFAULT_REQUEST, run_mx_skills_adapter  # noqa: E402


def has_real_mx_environment() -> bool:
    return (
        os.environ.get("RUN_REAL_MX_INTEGRATION") == "1"
        and os.environ.get("MX_ALLOW_REAL_PROVIDER", "").lower() == "true"
        and bool(os.environ.get("MX_APIKEY"))
        and bool(os.environ.get("MX_SKILLS_BASE_URL") or os.environ.get("MX_BASE_URL"))
    )


@unittest.skipUnless(has_real_mx_environment(), "Real MX integration requires explicit local environment gates.")
class ManualRealMXAdapterIntegrationTest(unittest.TestCase):
    def test_manual_real_provider_result_has_safe_shape(self) -> None:
        result = run_mx_skills_adapter(
            request=DEFAULT_REQUEST,
            user_id="balanced_user",
            adapter_mode="real-mx",
            allow_real_provider=True,
            capabilities=["mx-xuangu"],
        )

        self.assertIn(result["status"], {"completed", "blocked"})
        self.assertTrue(result["real_provider_attempted"])
        self.assertTrue(result["safety_gate"]["api_key_present"])
        self.assertFalse(result["safety_gate"]["raw_response_persisted"])
        self.assertIn("risk_disclosure", result)
        self.assertGreaterEqual(len(result["adapter_trace"]), 1)
        self.assertFalse(result["adapter_trace"][0]["raw_response_persisted"])


if __name__ == "__main__":
    unittest.main()
