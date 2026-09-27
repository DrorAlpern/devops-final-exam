#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 ci/install-tools.py --kubernetes
cluster_config="$HOME/.config/devops-submission/kubeconfig"
install -d -m 700 "$(dirname "$cluster_config")"
kind_cmd=(.tools/bin/kind)
if ! docker info > /dev/null 2>&1; then kind_cmd=(sudo -n .tools/bin/kind); fi
if "${kind_cmd[@]}" get clusters | grep -qx devops-submission; then
  echo 'The devops-submission cluster already exists. Reusing its configuration.'
  "${kind_cmd[@]}" export kubeconfig --name devops-submission --kubeconfig "$cluster_config"
else
  "${kind_cmd[@]}" create cluster --config lab/kind-config.yaml \
    --kubeconfig "$cluster_config" --wait 120s
fi
if [[ ${kind_cmd[0]} == sudo ]]; then
  sudo -n chown "$(id -u):$(id -g)" "$cluster_config"
fi
chmod 600 "$cluster_config"
.tools/bin/kubectl --kubeconfig "$cluster_config" --context kind-devops-submission \
  wait --for=condition=Ready node --all --timeout=120s
# Node readiness alone does not prove DNS, Service routing, or storage works.
.tools/bin/kubectl --kubeconfig "$cluster_config" --context kind-devops-submission \
  -n kube-system rollout status daemonset/kube-proxy --timeout=180s
.tools/bin/kubectl --kubeconfig "$cluster_config" --context kind-devops-submission \
  -n kube-system rollout status deployment/coredns --timeout=180s
.tools/bin/kubectl --kubeconfig "$cluster_config" --context kind-devops-submission \
  -n local-path-storage rollout status deployment/local-path-provisioner --timeout=180s
printf 'Cluster ready. Configuration: %s\n' "$cluster_config"
