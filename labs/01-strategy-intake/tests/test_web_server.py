import json
import os
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer


WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
sys.path.insert(0, WEB_DIR)

from server import StrategyIntakeHandler  # noqa: E402


class StrategyIntakeWebServerTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), StrategyIntakeHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()

    def post_json(self, path, payload):
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.read().decode("utf-8")

    def test_parse_stream_returns_stages_and_result(self):
        body = self.post_json(
            "/api/parse-stream",
            {
                "mode": "rules",
                "request": "找最近 60 日趋势较强、回撤较低的电网设备方向股票，生成候选观察池。",
            },
        )

        self.assertIn("event: stage", body)
        self.assertIn('"stage": "baseline"', body)
        self.assertIn('"stage": "route"', body)
        self.assertIn("event: result", body)
        self.assertIn('"provider": "rules"', body)


if __name__ == "__main__":
    unittest.main()
