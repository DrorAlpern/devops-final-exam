#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/bin:$PWD/.venv/bin:$PATH"
version=${KUBERNETES_VERSION:-1.35.0}
chart=helm/flask-aws-monitor
mkdir -p reports
helm lint "$chart" --strict
helm template monitor "$chart" --namespace devops-monitor > reports/helm-default.yaml
helm template monitor "$chart" --namespace devops-monitor \
  --set replicaCount=3 --set image.tag=b07205ae146d \
  --set service.port=8080 --set service.type=LoadBalancer \
  --set ingress.enabled=true --set ingress.host=monitor.example.com \
  --set ingress.className=nginx --set resources.limits.memory=768Mi \
  > reports/helm-custom.yaml
kubeconform -strict -summary -kubernetes-version "$version" \
  k8s/namespace.yaml k8s/deployment.yaml k8s/service.yaml \
  ci/local-kubernetes/preview-ingress.yaml \
  reports/helm-default.yaml reports/helm-custom.yaml
if helm template invalid "$chart" --set replicaCount=0 > /dev/null 2>&1; then
  echo 'Invalid replica count was unexpectedly accepted.' >&2; exit 1
fi
if helm template invalid "$chart" --set ingress.enabled=true > /dev/null 2>&1; then
  echo 'Ingress without a host was unexpectedly accepted.' >&2; exit 1
fi
echo 'Invalid replica count and missing Ingress host correctly rejected.'
