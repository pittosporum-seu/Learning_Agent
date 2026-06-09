import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from tool_registry import build_default_registry  # noqa: E402


class ToolRegistryTests(unittest.TestCase):
    def test_registry_contains_three_mock_tools(self):
        registry = build_default_registry()

        tool_names = {tool["name"] for tool in registry.list_tools()}

        self.assertEqual(
            tool_names,
            {"select_candidates", "fetch_market_data", "search_finance_news"},
        )
        for name in tool_names:
            self.assertEqual(registry.get(name).provider, "local-mock")


if __name__ == "__main__":
    unittest.main()
