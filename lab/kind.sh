#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/bin:$PATH"
export KUBECONFIG="$HOME/.config/devops-submission/kubeconfig"
docker_cmd=(docker)
if ! docker info > /dev/null 2>&1; then docker_cmd=(sudo -n docker); fi
k() { kubectl --context kind-devops-submission -n devops-submission "$@"; }
h() { helm --kube-context kind-devops-submission -n devops-submission "$@"; }
case "${1:-}" in
  up)
    bash lab/start-kind.sh
    # Content hash also changes when the working tree has uncommitted app edits.
    tag=$(find app -type f ! -path '*/__pycache__/*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-12)
    image="droralpern/flask-aws-monitor:local-$tag"
    "${docker_cmd[@]}" build -t "$image" app
    if [[ ${docker_cmd[0]} == sudo ]]; then
      sudo -n .tools/bin/kind load docker-image --name devops-submission "$image"
    else
      kind load docker-image --name devops-submission "$image"
    fi
    k apply -f lab/k8s/namespace.yaml -f lab/k8s/moto.yaml
    k rollout status deployment/moto --timeout=180s
    k create configmap terraform-config --from-file=lab/terraform/main.tf \
      --from-file=lab/terraform/versions.tf --from-file=lab/terraform/.terraform.lock.hcl \
      --dry-run=client -o yaml | k apply -f -
    k delete job terraform-local --ignore-not-found --wait=true
    k apply -f lab/k8s/terraform.yaml
    if ! k wait --for=condition=complete job/terraform-local --timeout=600s; then
      k logs job/terraform-local; exit 1
    fi
    k logs job/terraform-local
    k apply -f lab/k8s/service.yaml
    kubectl set image --local -f lab/k8s/monitor.yaml "monitor=$image" -o yaml | k apply -f -
    k rollout status deployment/monitor --timeout=180s
    k exec -i deployment/monitor -- python - < lab/verify.py
    k create secret generic local-aws --from-literal=AWS_ACCESS_KEY_ID=local-lab \
      --from-literal=AWS_SECRET_ACCESS_KEY=local-lab --dry-run=client -o yaml | k apply -f -
    h upgrade --install monitor-helm helm/flask-aws-monitor --wait --timeout 180s \
      --set "image.tag=local-$tag" --set image.pullPolicy=IfNotPresent \
      --set aws.existingSecret=local-aws --set extraEnv.AWS_ENDPOINT_URL=http://moto:5000
    k exec -i deployment/monitor-helm -- python - < lab/verify.py
    echo 'Local Kubernetes application ready. See lab/README.md for port-forwarding.'
    ;;
  verify)
    k exec -i deployment/monitor -- python - < lab/verify.py
    old_uid=$(k get pods -l app=submission-monitor -o jsonpath='{.items[0].metadata.uid}')
    k delete pod -l app=submission-monitor --wait=true
    k wait --for=condition=Ready pod -l app=submission-monitor --timeout=180s
    new_uid=$(k get pods -l app=submission-monitor -o jsonpath='{.items[0].metadata.uid}')
    [[ "$old_uid" != "$new_uid" ]]
    k exec -i deployment/monitor -- python - < lab/verify.py
    revision=$(h status monitor-helm -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')
    h upgrade monitor-helm helm/flask-aws-monitor --reuse-values --set replicaCount=2 --wait --timeout 180s
    k wait --for=jsonpath='{.status.readyReplicas}'=2 deployment/monitor-helm --timeout=180s
    k exec -i deployment/monitor-helm -- python - < lab/verify.py
    h rollback monitor-helm "$revision" --wait --timeout 180s
    k wait --for=jsonpath='{.status.readyReplicas}'=1 deployment/monitor-helm --timeout=180s
    k exec -i deployment/monitor-helm -- python - < lab/verify.py
    echo 'Pod recovery, Helm scale-up and rollback, and live emulator inventory passed.'
    ;;
  down) k delete namespace devops-submission --ignore-not-found ;;
  *) echo 'Usage: bash lab/kind.sh up|verify|down' >&2; exit 2 ;;
esac
