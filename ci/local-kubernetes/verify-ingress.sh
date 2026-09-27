#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PATH="$PWD/.tools/bin:$PATH"
export KUBECONFIG="$HOME/.config/devops-kubernetes/kubeconfig"
[[ "$(kubectl config current-context)" == kind-devops-local ]] || {
  echo 'Ingress verification is restricted to the local lab.' >&2; exit 1;
}
[[ "$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')" == https://127.0.0.1:16443 ]] || {
  echo 'Refusing to use a non-local Kubernetes API.' >&2; exit 1;
}
mkdir -p reports
kubectl -n devops-ingress port-forward service/lab-traefik 15004:80 \
  --address 127.0.0.1 > reports/ingress-forward.log 2>&1 &
forward_pid=$!
cleanup() {
  kill "$forward_pid" 2>/dev/null || true
  wait "$forward_pid" 2>/dev/null || true
}
trap cleanup EXIT
python3 ci/local-kubernetes/check_ingress.py
