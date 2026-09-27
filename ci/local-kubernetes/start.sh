#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 ci/install-tools.py --kubernetes
cluster_config="$HOME/.config/devops-kubernetes/kubeconfig"
install -d -m 700 "$(dirname "$cluster_config")"
kind_cmd=(.tools/bin/kind)
if ! docker info > /dev/null 2>&1; then kind_cmd=(sudo -n .tools/bin/kind); fi
if "${kind_cmd[@]}" get clusters | grep -qx devops-local; then
  echo 'The devops-local cluster already exists. Reusing its configuration.'
  "${kind_cmd[@]}" export kubeconfig --name devops-local --kubeconfig "$cluster_config"
else
  "${kind_cmd[@]}" create cluster --config ci/local-kubernetes/kind.yaml \
    --kubeconfig "$cluster_config" --wait 120s
fi
if [[ ${kind_cmd[0]} == sudo ]]; then
  sudo -n chown "$(id -u):$(id -g)" "$cluster_config"
fi
chmod 600 "$cluster_config"
.tools/bin/kubectl --kubeconfig "$cluster_config" --context kind-devops-local \
  wait --for=condition=Ready node --all --timeout=120s
printf 'Cluster ready. Configuration: %s\n' "$cluster_config"
