"""Serve the built web app with local API forwarding for browser acceptance.

Run from the repository root after ``npm run build`` in apps/web:
    python scripts/phase4_preview_server.py
This server is for local verification only; it does not write uploaded data.
"""
from __future__ import annotations

import argparse
import http.client
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "apps" / "web" / "dist"


class Handler(BaseHTTPRequestHandler):
    backend_port = 8000

    def _proxy(self):
        parsed = urlsplit(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else None
        connection = http.client.HTTPConnection("127.0.0.1", self.backend_port, timeout=180)
        headers = {key: value for key, value in self.headers.items()
                   if key.lower() not in {"host", "connection", "content-length"}}
        try:
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()
            payload = response.read()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length", "content-encoding"}:
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except OSError as exc:
            message = f"Local backend unavailable: {exc}".encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)
        finally:
            connection.close()

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == "/api" or parsed.path.startswith(("/api/", "/uploads/", "/artifacts/")):
            return self._proxy()
        relative = parsed.path.lstrip("/") or "index.html"
        file_path = (DIST / relative).resolve()
        if not file_path.is_relative_to(DIST.resolve()) or not file_path.is_file():
            self.send_error(404)
            return
        payload = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if urlsplit(self.path).path.startswith("/api/"):
            return self._proxy()
        self.send_error(404)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5173)
    parser.add_argument("--backend-port", type=int, default=8000)
    args = parser.parse_args()
    if not DIST.joinpath("index.html").is_file():
        parser.error("apps/web/dist is missing; run npm run build in apps/web")
    Handler.backend_port = args.backend_port
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Phase 4 preview on http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()
