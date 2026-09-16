"""Check the two lab hosts through the local Ingress controller."""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:15004"
ROOT = Path(__file__).resolve().parents[2]


def request(host, path):
    # The fixed loopback URL receives only non-secret lab hostnames.
    req = urllib.request.Request(BASE + path, headers={"Host": host})
    try:
        response = urllib.request.urlopen(req, timeout=5)  # nosec B310
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.read().decode(), dict(response.headers)


def main():
    for attempt in range(30):
        try:
            status, _, _ = request("monitor.localhost", "/healthz")
            if status == 200:
                break
        except (urllib.error.URLError, TimeoutError, ConnectionResetError):
            pass
        if attempt == 29:
            raise SystemExit("The Ingress health route did not become ready.")
        time.sleep(1)

    checks = [
        ("monitor.localhost", "/healthz", 200, '"status":"ok"'),
        ("monitor.localhost", "/", 503, "AWS resources are unavailable"),
        ("preview.localhost", "/", 200, "all resources below are sample data"),
        ("preview.localhost", "/static/style.css", 200, ".masthead"),
        ("unconfigured.localhost", "/", 404, "404 page not found"),
    ]
    results = []
    for host, path, expected, content in checks:
        status, body, headers = request(host, path)
        if status != expected or content not in body:
            raise SystemExit(f"Unexpected Ingress response: {host}{path}, HTTP {status}.")
        if host == "monitor.localhost" and "all resources below are sample data" in body:
            raise SystemExit("The production route unexpectedly returned sample data.")
        if host == "preview.localhost" and path == "/":
            if headers.get("X-Content-Type-Options") != "nosniff":
                raise SystemExit("Application security headers did not reach the browser.")
        results.append({"host": host, "path": path, "status": status, "content_check": "passed"})
        print(f"{host}{path}: HTTP {status}; expected content confirmed.")
    report = {"environment": "Local kind cluster; no AWS account connected", "checks": results}
    (ROOT / "reports" / "ingress-local.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
