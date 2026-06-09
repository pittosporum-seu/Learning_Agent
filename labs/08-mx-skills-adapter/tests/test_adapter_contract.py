from __future__ import annotations

import sys
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from adapter_contract import AdapterResult, validate_adapter_result  # noqa: E402
from adapter_registry import build_default_registry  # noqa: E402


class AdapterContractTest(unittest.TestCase):
    def test_adapter_result_has_required_fields(self) -> None:
        result = AdapterResult(
            adapter_name="mock-mx",
            provider_mode="mock",
            capability="mx-data",
            input_summary={},
            output={},
            status="success",
            error=None,
            requires_api_key=False,
            requires_human_confirmation=False,
        ).to_dict()

        self.assertTrue(validate_adapter_result(result))

    def test_registry_lists_mock_and_real_stub(self) -> None:
        registry = build_default_registry()
        adapter_names = {adapter["adapter_name"] for adapter in registry.list_adapters()}

        self.assertEqual(adapter_names, {"mock-mx", "real-mx-stub"})


if __name__ == "__main__":
    unittest.main()
