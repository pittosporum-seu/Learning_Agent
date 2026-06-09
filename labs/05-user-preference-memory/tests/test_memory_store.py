import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from memory_store import UnknownUserError, build_memory_snapshot, load_user_preferences  # noqa: E402


class MemoryStoreTests(unittest.TestCase):
    def test_loads_conservative_and_balanced_users(self):
        profiles = load_user_preferences()

        self.assertIn("conservative_user", profiles)
        self.assertIn("balanced_user", profiles)
        self.assertEqual(profiles["conservative_user"]["max_candidates"], 1)
        self.assertEqual(profiles["balanced_user"]["max_candidates"], 2)

    def test_build_memory_snapshot_includes_events(self):
        snapshot = build_memory_snapshot("conservative_user")

        self.assertEqual(snapshot["user_id"], "conservative_user")
        self.assertEqual(snapshot["base_profile"]["risk_level"], "low")
        self.assertGreaterEqual(snapshot["event_count"], 1)
        self.assertIn("privacy_note", snapshot)

    def test_unknown_user_raises_clear_error(self):
        with self.assertRaisesRegex(UnknownUserError, "Unknown mock user_id"):
            build_memory_snapshot("missing_user")


if __name__ == "__main__":
    unittest.main()
