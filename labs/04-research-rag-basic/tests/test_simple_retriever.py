import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)

from document_loader import load_documents  # noqa: E402
from simple_retriever import retrieve  # noqa: E402


class SimpleRetrieverTests(unittest.TestCase):
    def test_retriever_can_hit_risk_policy_and_report_template(self):
        chunks = load_documents()
        results = retrieve(
            query="risk_disclosure negative_news report_template source chunk_id matched_terms used_for 观察池 报告 风险",
            chunks=chunks,
            top_k=6,
        )

        sources = {item["source"] for item in results}
        self.assertIn("risk_policy.md", sources)
        self.assertIn("report_template.md", sources)
        self.assertTrue(all(item["matched_terms"] for item in results))
        self.assertTrue(all(item["score"] > 0 for item in results))


if __name__ == "__main__":
    unittest.main()
