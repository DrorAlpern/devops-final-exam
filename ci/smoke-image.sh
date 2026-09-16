#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_NAME:?Set IMAGE_NAME to the Docker image repository}"
: "${IMAGE_TAG:?Set IMAGE_TAG to the image tag}"

image="${IMAGE_NAME}:${IMAGE_TAG}"
container_id=""

cleanup() {
  if [[ -n "$container_id" ]]; then
    docker rm -f "$container_id" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# No published ports, host credentials, or network access are needed for this check.
container_id=$(docker run -d --rm --network none --read-only \
  --tmpfs /tmp:rw,nosuid,noexec,size=64m \
  --cap-drop ALL --security-opt no-new-privileges \
  --env AWS_EC2_METADATA_DISABLED=true \
  --env AWS_ACCESS_KEY_ID= --env AWS_SECRET_ACCESS_KEY= --env AWS_SESSION_TOKEN= \
  "$image")

# Probe localhost from inside the container, so the CI agent needs only Docker.
docker exec -i "$container_id" python - <<'PY'
import sys
import time
import urllib.error
import urllib.request

base_url = "http://127.0.0.1:5001"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(path):
    try:
        with opener.open(base_url + path, timeout=2) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


for _ in range(30):
    try:
        health_status, _ = fetch("/healthz")
    except urllib.error.URLError:
        time.sleep(1)
        continue
    if health_status != 200:
        sys.exit(f"FAIL: /healthz returned HTTP {health_status}; expected 200.")
    break
else:
    sys.exit("FAIL: /healthz did not become available within 30 seconds.")

try:
    inventory_status, body = fetch("/")
except urllib.error.URLError:
    sys.exit("FAIL: The inventory endpoint did not respond.")

if inventory_status != 503:
    sys.exit(f"FAIL: / returned HTTP {inventory_status}; expected 503 without AWS access.")
if "Unable to load AWS inventory" not in body or "AWS resources are unavailable" not in body:
    sys.exit("FAIL: The inventory error does not contain the expected helpful message.")
if "Traceback" in body:
    sys.exit("FAIL: The inventory response exposes a Python traceback.")

print("PASS: /healthz returned 200; / returned a helpful 503 without a traceback.")
PY
