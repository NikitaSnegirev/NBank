from __future__ import annotations

import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


DEFAULT_RESPONSE = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.2,
    "reason": "Mocked fraud decision",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

STATE_LOCK = threading.Lock()
STATE: dict[str, Any] = {
    "endpoint": r"/.*",
    "response_body": DEFAULT_RESPONSE,
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def _send_json(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _current_state(self) -> tuple[str, dict[str, Any]]:
        with STATE_LOCK:
            return str(STATE["endpoint"]), dict(STATE["response_body"])

    def _reply_fraud_decision(self) -> None:
        endpoint, response_body = self._current_state()
        path_re = re.compile(endpoint)

        if not path_re.fullmatch(self.path) and not path_re.match(self.path):
            self._send_json(404, {"error": "not found"})
            return

        self._send_json(200, response_body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/__admin/health":
            self._send_json(200, {"status": "UP"})
            return
        if self.path == "/__admin/config":
            endpoint, response_body = self._current_state()
            self._send_json(200, {"endpoint": endpoint, "response_body": response_body})
            return

        self._reply_fraud_decision()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/__admin/config":
            body = self._read_json()
            with STATE_LOCK:
                STATE["endpoint"] = body.get("endpoint", r"/.*")
                STATE["response_body"] = body.get("response_body", DEFAULT_RESPONSE)
            self._send_json(200, {"status": "configured"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length:
                self.rfile.read(length)
        except Exception:
            pass

        self._reply_fraud_decision()


def main() -> None:
    host = os.getenv("FRAUD_MOCK_HOST", "0.0.0.0")
    port = int(os.getenv("FRAUD_MOCK_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
