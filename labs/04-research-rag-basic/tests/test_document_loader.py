import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from document_loader import load_documents  # noqa: E402


class DocumentLoaderTests(unittest.TestCase):
    def test_load_documents_splits_markdown_into_chunks(self):
        chunks = load_documents()

        self.assertGreaterEqual(len(chunks), 6)
        first = chunks[0]
        self.assertIn("chunk_id", first)
        self.assertIn("source", first)
        self.assertIn("section", first)
        self.assertIn("content", first)
        self.assertIn("keywords", first)
        self.assertTrue(any(chunk["source"] == "risk_policy.md" for chunk in chunks))
        self.assertTrue(any(chunk["source"] == "report_template.md" for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
