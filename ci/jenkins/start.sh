#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export JENKINS_SECRET_DIR="${JENKINS_SECRET_DIR:-$HOME/.config/devops-jenkins}"
export DOCKER_CONFIG_DIR="${DOCKER_CONFIG_DIR:-$HOME/.docker}"
export DOCKER_GID
DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)
umask 077
mkdir -p "$JENKINS_SECRET_DIR"
if [[ ! -s "$JENKINS_SECRET_DIR/admin_password" ]]; then
  python3 -c 'import secrets; print(secrets.token_urlsafe(24), end="")' \
    > "$JENKINS_SECRET_DIR/admin_password"
fi
touch "$JENKINS_SECRET_DIR/agent_secret"
[[ -s "$DOCKER_CONFIG_DIR/config.json" ]] || {
  echo 'Run docker login as your normal user before starting Jenkins.' >&2; exit 1
}
compose() {
  sudo -n env JENKINS_SECRET_DIR="$JENKINS_SECRET_DIR" \
    DOCKER_CONFIG_DIR="$DOCKER_CONFIG_DIR" DOCKER_GID="$DOCKER_GID" \
    docker compose -f ci/jenkins/compose.yaml "$@"
}
compose build
compose up -d controller
python3 ci/jenkins/bootstrap.py
compose up -d agent
echo 'Jenkins is available at http://127.0.0.1:18080 on this machine.'
