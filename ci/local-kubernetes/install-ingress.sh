#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PATH="$PWD/.tools/bin:$PATH"
export KUBECONFIG="$HOME/.config/devops-kubernetes/kubeconfig"
[[ "$(kubectl config current-context)" == kind-devops-local ]] || {
  echo 'This setup is restricted to the local lab.' >&2; exit 1;
}
[[ "$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')" == https://127.0.0.1:16443 ]] || {
  echo 'Refusing to use a non-local Kubernetes API.' >&2; exit 1;
}
# The raw and Helm verification exercise creates these namespaces and the existing Secret.
kubectl get namespace devops-helm-local devops-preview > /dev/null
kubectl -n devops-preview get service monitor-preview > /dev/null
helm status monitor -n devops-helm-local > /dev/null
chart=.tools/traefik-41.5.0.tgz
checksum=30f8db73182019b2764179d7fc0a7efc9505670204f847ffc3a779bacaae3a1a
if [[ ! -f "$chart" ]]; then
  curl --fail --silent --show-error --location \
    https://traefik.github.io/charts/traefik/traefik-41.5.0.tgz --output "$chart"
fi
printf '%s  %s\n' "$checksum" "$chart" | sha256sum --check
helm upgrade --install lab-traefik "$chart" --namespace devops-ingress --create-namespace \
  --skip-crds --values ci/local-kubernetes/traefik-values.yaml --wait --timeout 180s
helm upgrade monitor helm/flask-aws-monitor -n devops-helm-local --reuse-values \
  --set ingress.enabled=true --set ingress.className=lab-traefik \
  --set ingress.host=monitor.localhost --wait --timeout 180s
kubectl apply -f ci/local-kubernetes/preview-ingress.yaml
kubectl -n devops-ingress rollout status deployment/lab-traefik --timeout=120s
echo 'Local Ingress routes are configured. Run ci/local-kubernetes/verify-ingress.sh next.'
