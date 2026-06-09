from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from real_mx_adapter_stub import REAL_PROVIDER_DISABLED_REASON, RealMXAdapterStub  # noqa: E402


class RealMXAdapterStubTest(unittest.TestCase):
    def test_real_adapter_stub_is_blocked_without_network_or_key(self) -> None:
        result = RealMXAdapterStub().call("mx-data", {"candidate_ids": ["MOCK_GRID_001"]})

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["error"], REAL_PROVIDER_DISABLED_REASON)
        self.assertFalse(result["output"]["network_request_sent"])
        self.assertFalse(result["output"]["api_key_read"])
        self.assertTrue(result["requires_api_key"])
        self.assertTrue(result["requires_human_confirmation"])


if __name__ == "__main__":
    unittest.main()
