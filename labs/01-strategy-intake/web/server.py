from __future__ import annotations

import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


WEB_DIR = Path(__file__).resolve().parent
LAB_ROOT = WEB_DIR.parent
SRC_DIR = LAB_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from mimo_strategy_intake import (  # noqa: E402
    MimoConfigError,
    MimoResponseError,
    get_mimo_status,
    parse_strategy_request_with_mimo,
)
from strategy_intake import DEFAULT_REQUEST, parse_strategy_request  # noqa: E402


class StrategyIntakeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/api/health":
            self.send_json(
                {
                    "status": "ok",
                    "lab": "01-strategy-intake",
                    "mimo": get_mimo_status(),
                    "modes": ["rules", "mimo"],
                }
            )
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in ("/api/parse", "/api/parse-stream"):
            self.send_error(404, "Not found")
            return

        try:
            payload = self.read_json_body()
            request = str(payload.get("request") or DEFAULT_REQUEST)
            mode = str(payload.get("mode") or "rules").strip().lower()
            if parsed.path == "/api/parse-stream":
                self.stream_parse(request, mode)
                return

            if mode == "mimo":
                self.send_json(parse_strategy_request_with_mimo(request))
                return

            spec = parse_strategy_request(request).to_dict()
            self.send_json({"provider": "rules", "strategy_spec": spec})
        except MimoConfigError as exc:
            self.send_json({"error": str(exc), "provider": "mimo"}, status=400)
        except MimoResponseError as exc:
            self.send_json({"error": str(exc), "provider": "mimo"}, status=502)
        except Exception as exc:  # pragma: no cover - demo server guardrail
            self.send_json({"error": str(exc)}, status=500)

    def stream_parse(self, request: str, mode: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        try:
            self.send_sse("stage", {"stage": "intake", "message": "读取自然语言策略", "progress": 12})
            time.sleep(0.08)
            self.send_sse("stage", {"stage": "baseline", "message": "生成规则基线 StrategySpec", "progress": 30})

            if mode == "mimo":
                self.send_sse("stage", {"stage": "mimo", "message": "调用 MiMo 做语义补全", "progress": 55})
                result = parse_strategy_request_with_mimo(request)
                self.send_sse("stage", {"stage": "merge", "message": "合并模型结果与规则基线", "progress": 78})
            else:
                result = {"provider": "rules", "strategy_spec": parse_strategy_request(request).to_dict()}
                self.send_sse("stage", {"stage": "merge", "message": "整理规则解析结果", "progress": 78})

            time.sleep(0.08)
            self.send_sse("stage", {"stage": "safety", "message": "补齐风险提示和安全边界", "progress": 92})
            self.send_sse("result", result)
            self.send_sse("stage", {"stage": "done", "message": "解析完成", "progress": 100})
        except MimoConfigError as exc:
            self.send_sse("error", {"error": str(exc), "provider": "mimo"})
        except MimoResponseError as exc:
            self.send_sse("error", {"error": str(exc), "provider": "mimo"})
        except Exception as exc:  # pragma: no cover - demo server guardrail
            self.send_sse("error", {"error": str(exc)})

    def read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)
        if not raw_body:
            return {}
        return json.loads(raw_body.decode("utf-8"))

    def send_file(self, path: Path, content_type: str) -> None:
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload: dict[str, object], status: int = 200) -> None:
        content = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_sse(self, event_name: str, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False)
        content = f"event: {event_name}\ndata: {body}\n\n".encode("utf-8")
        self.wfile.write(content)
        self.wfile.flush()

    def log_message(self, format: str, *args: object) -> None:
        print(f"[web] {self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lab 01 Strategy Intake web demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), StrategyIntakeHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Lab 01 Strategy Intake web demo running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping web demo.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
