from __future__ import annotations

import json
import os
import re
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional

import pytest
import requests


@dataclass(frozen=True)
class FraudMockConfig:
    port: int = 8080
    endpoint: str = r"/.*"
    response_body: dict[str, Any] = None  # set by loader


class _ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def _load_fraud_mock_config(request: pytest.FixtureRequest) -> Optional[FraudMockConfig]:
    mark = request.node.get_closest_marker("fraud_check_mock")
    if not mark:
        return None

    kwargs = dict(mark.kwargs or {})
    port = int(kwargs.pop("port", 8080))
    endpoint = str(kwargs.pop("endpoint", r"/.*"))

    # Remaining kwargs form the response JSON body. Provide safe defaults if not specified.
    body = {
        "status": kwargs.pop("status", "SUCCESS"),
        "decision": kwargs.pop("decision", "APPROVED"),
        "riskScore": kwargs.pop("riskScore", 0.2),
        "reason": kwargs.pop("reason", "Mocked fraud decision"),
        "requiresManualReview": kwargs.pop("requiresManualReview", False),
        "additionalVerificationRequired": kwargs.pop("additionalVerificationRequired", False),
        **kwargs,
    }

    return FraudMockConfig(port=port, endpoint=endpoint, response_body=body)


@pytest.fixture(scope="function")
def fraud_check_mock_server(request: pytest.FixtureRequest):
    """
    Marker-driven local HTTP mock for FraudCheck service.

    Why real HTTP server: the fraud integration is executed by the backend, not by Python code.
    """
    cfg = _load_fraud_mock_config(request)
    if cfg is None:
        yield
        return

    admin_url = os.getenv("FRAUD_MOCK_ADMIN_URL")
    if admin_url:
        response = requests.post(
            admin_url,
            json={
                "endpoint": cfg.endpoint,
                "response_body": cfg.response_body,
            },
            timeout=5,
        )
        response.raise_for_status()
        yield
        return

    path_re = re.compile(cfg.endpoint)
    response_bytes = json.dumps(cfg.response_body).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # pragma: no cover
            # Silence default noisy server logging in pytest output.
            return

        def _reply(self) -> None:
            # For robustness: answer both GET/POST. Backend images may probe with GET.
            if not path_re.fullmatch(self.path) and not path_re.match(self.path):
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"not found"}')
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response_bytes)

        def do_GET(self) -> None:  # noqa: N802
            self._reply()

        def do_POST(self) -> None:  # noqa: N802
            # Read & ignore request body (backend may send JSON).
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length:
                    _ = self.rfile.read(length)
            except Exception:
                pass
            self._reply()

    servers: list[_ReusableHTTPServer] = []
    threads: list[threading.Thread] = []
    bound_ports: list[int] = []

    # Try a small set of commonly hardcoded ports too (robustness for different backend builds).
    for p in (cfg.port, 8080, 8089):
        p = int(p)
        if p in bound_ports:
            continue
        try:
            srv = _ReusableHTTPServer(("0.0.0.0", p), Handler)
        except OSError:
            continue

        t = threading.Thread(target=srv.serve_forever, name=f"fraud-mock:{p}", daemon=True)
        t.start()
        servers.append(srv)
        threads.append(t)
        bound_ports.append(p)

    if not servers:
        raise RuntimeError(
            f"Failed to start Fraud mock server on any of ports: {(cfg.port, 8080, 8089)}. "
            f"Free the port(s) or pick another via @pytest.mark.fraud_check_mock(port=...)."
        )

    try:
        yield
    finally:
        for srv in servers:
            try:
                srv.shutdown()
            except Exception:
                pass
            try:
                srv.server_close()
            except Exception:
                pass
