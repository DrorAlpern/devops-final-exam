#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PATH="$PWD/.tools/bin:$PATH"
export KUBECONFIG="$HOME/.config/devops-kubernetes/kubeconfig"
[[ "$(kubectl config current-context)" == kind-devops-local ]] || {
  echo 'This preview is restricted to the local lab.' >&2; exit 1;
}
kubectl create namespace devops-preview --dry-run=client -o yaml | kubectl apply -f -
kubectl -n devops-preview create configmap monitor-preview \
  --from-file=demo_wsgi.py=tests/demo_wsgi.py --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f ci/local-kubernetes/preview.yaml
kubectl -n devops-preview rollout status deployment/monitor-preview --timeout=180s
echo 'Sample-data preview: http://127.0.0.1:15003 (leave this process running).'
exec kubectl -n devops-preview port-forward service/monitor-preview 15003:5001 --address 127.0.0.1
