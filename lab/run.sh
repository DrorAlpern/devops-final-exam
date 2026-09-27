#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker_cmd=(docker)
if ! docker info > /dev/null 2>&1; then docker_cmd=(sudo -n docker); fi
compose=("${docker_cmd[@]}" compose -f lab/compose.yaml)
verify() {
  "${compose[@]}" exec -T monitor python /checks/verify.py
  # Exercise the published port from the Linux host network as well.
  "${docker_cmd[@]}" run --rm --network host --entrypoint python \
    droralpern/flask-aws-monitor:local-lab -c \
    'import urllib.request; r=urllib.request.urlopen("http://127.0.0.1:15005/", timeout=20); assert r.status == 200; assert b"Local AWS API lab" in r.read(); print("Published host port: HTTP 200")'
}
case "${1:-}" in
  up)
    "${compose[@]}" up -d --wait moto
    "${compose[@]}" run --rm terraform init -input=false -lockfile=readonly
    "${compose[@]}" run --rm terraform apply -input=false -auto-approve
    "${compose[@]}" up -d --build --wait monitor
    verify
    echo 'Local inventory: http://127.0.0.1:15005'
    ;;
  verify) verify ;;
  plan) "${compose[@]}" run --rm terraform plan -input=false -detailed-exitcode ;;
  down)
    # Deletes only this Compose project's disposable emulator data/state.
    "${compose[@]}" down --volumes
    ;;
  *) echo 'Usage: bash lab/run.sh up|verify|plan|down' >&2; exit 2 ;;
esac
