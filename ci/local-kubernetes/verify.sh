#!/usr/bin/env bash
# Exercise only the dedicated local cluster; no AWS credentials are supplied.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PATH="$PWD/.tools/bin:$PATH"
export KUBECONFIG="$HOME/.config/devops-kubernetes/kubeconfig"
[[ "$(kubectl config current-context)" == kind-devops-local ]] || {
  echo 'Refusing to run outside the local lab context.' >&2; exit 1;
}
[[ "$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')" == https://127.0.0.1:16443 ]] || {
  echo 'Refusing to use a non-local Kubernetes API.' >&2; exit 1;
}
mkdir -p reports
forward_pid=''
cleanup() {
  if [[ -n "$forward_pid" ]]; then
    kill "$forward_pid" 2>/dev/null || true
    wait "$forward_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT
empty_credentials() {
  kubectl -n "$1" create secret generic aws-credentials \
    --from-literal=AWS_ACCESS_KEY_ID= --from-literal=AWS_SECRET_ACCESS_KEY= \
    --dry-run=client -o yaml | kubectl apply -f -
}
check_http() {
  local namespace=$1 service=$2 port=$3 ready=false code
  kubectl -n "$namespace" port-forward "service/$service" "$port:5001" \
    --address 127.0.0.1 > "reports/$namespace-forward.log" 2>&1 &
  forward_pid=$!
  for _ in {1..30}; do
    if curl --fail --silent "http://127.0.0.1:$port/healthz" > /dev/null; then
      ready=true; break
    fi
    sleep 1
  done
  [[ "$ready" == true ]] || { echo 'Health endpoint did not become ready.' >&2; exit 1; }
  code=$(curl --silent --show-error --output "reports/$namespace-inventory.html" \
    --write-out '%{http_code}' "http://127.0.0.1:$port/")
  [[ "$code" == 503 ]] || { echo "Expected inventory 503 without AWS, got $code" >&2; exit 1; }
  printf '%s: health 200; inventory 503 without AWS credentials\n' "$namespace"
  cleanup
  forward_pid=''
}
kubectl apply -f k8s/namespace.yaml
empty_credentials devops-monitor
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl -n devops-monitor rollout status deployment/flask-aws-monitor --timeout=180s
check_http devops-monitor flask-aws-monitor 15001
old_uid=$(kubectl -n devops-monitor get pods -l app=flask-aws-monitor -o jsonpath='{.items[0].metadata.uid}')
kubectl -n devops-monitor delete pod -l app=flask-aws-monitor --wait=true
kubectl -n devops-monitor wait --for=condition=Ready pod -l app=flask-aws-monitor --timeout=120s
new_uid=$(kubectl -n devops-monitor get pods -l app=flask-aws-monitor -o jsonpath='{.items[0].metadata.uid}')
[[ "$new_uid" != "$old_uid" ]] || { echo 'The failed pod was not replaced.' >&2; exit 1; }
echo 'Deployment replaced the deleted pod and restored readiness.'

kubectl create namespace devops-helm-local --dry-run=client -o yaml | kubectl apply -f -
empty_credentials devops-helm-local
helm upgrade --install monitor helm/flask-aws-monitor -n devops-helm-local \
  --set image.tag=b07205ae146d --set replicaCount=1 --wait --timeout 180s
baseline=$(helm status monitor -n devops-helm-local -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')
check_http devops-helm-local monitor 15002
helm upgrade monitor helm/flask-aws-monitor -n devops-helm-local \
  --set image.tag=a56aa0c325f4 --set replicaCount=3 --wait --timeout 180s
[[ "$(kubectl -n devops-helm-local get deployment monitor -o jsonpath='{.status.readyReplicas}')" == 3 ]]
[[ "$(kubectl -n devops-helm-local get deployment monitor -o jsonpath='{.spec.template.spec.containers[0].image}')" == droralpern/flask-aws-monitor:a56aa0c325f4 ]]
echo 'Helm upgrade: three ready replicas using the CI-published image.'
helm rollback monitor "$baseline" -n devops-helm-local --wait --timeout 180s
[[ "$(kubectl -n devops-helm-local get deployment monitor -o jsonpath='{.spec.replicas}')" == 1 ]]
[[ "$(kubectl -n devops-helm-local get deployment monitor -o jsonpath='{.status.readyReplicas}')" == 1 ]]
[[ "$(kubectl -n devops-helm-local get deployment monitor -o jsonpath='{.spec.template.spec.containers[0].image}')" == droralpern/flask-aws-monitor:b07205ae146d ]]
echo 'Helm rollback: one ready replica and the previous image restored.'
helm history monitor -n devops-helm-local -o json > reports/helm-local-history.json
kubectl get deployments -A -o json > reports/local-deployments.json
kubectl version -o json > reports/kubernetes-version.json
echo 'All local Kubernetes checks passed. Live AWS and remote deployment remain pending.'
