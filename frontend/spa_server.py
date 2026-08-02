import http.client
import http.server
import os
import sys
import urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3004
DIR = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath("dist")
BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "8000"))


def _proxy_api(path, method, headers, body):
    conn = http.client.HTTPConnection(BACKEND_HOST, BACKEND_PORT, timeout=30)
    try:
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        out_headers = {k: v for k, v in resp.getheaders() if k.lower() not in ("transfer-encoding", "connection", "keep-alive", "content-length")}
        return resp.status, out_headers, data
    finally:
        conn.close()


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isfile(path):
            return super().send_head()
        if self.path.startswith("/assets/"):
            return super().send_head()
        self.path = "/"
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _handle_api(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        out_headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "accept-encoding", "connection")}
        out_headers["Host"] = f"{BACKEND_HOST}:{BACKEND_PORT}"
        status, resp_headers, data = _proxy_api(self.path, self.command, out_headers, body)
        self.send_response(status)
        for k, v in resp_headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/health" or self.path.startswith("/api/"):
            return self._handle_api()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._handle_api()
        self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self._handle_api()
        self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self._handle_api()
        self.send_error(404)


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
        print(f"SPA server on :{PORT} serving {DIR} (api -> {BACKEND_HOST}:{BACKEND_PORT})", flush=True)
        httpd.serve_forever()
