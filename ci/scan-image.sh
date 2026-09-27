#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${IMAGE_NAME:?Set IMAGE_NAME to the Docker image repository}"
: "${IMAGE_TAG:?Set IMAGE_TAG to the commit tag}"
export PATH="$PWD/.tools/bin:$PATH"
mkdir -p reports
archive=$(mktemp "${TMPDIR:-/tmp}/monitor-image.XXXXXX.tar")
trap 'rm -f -- "$archive"' EXIT
docker image save "$IMAGE_NAME:$IMAGE_TAG" -o "$archive"
trivy image --input "$archive" --no-progress --scanners vuln --severity HIGH,CRITICAL \
  --exit-code 1 --format json --output reports/image-security.json
