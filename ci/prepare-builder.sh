#!/usr/bin/env bash
# Run only on the dedicated Ubuntu 24.04 course builder after AWS access is confirmed.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo on the course builder.' >&2; exit 1; }
# OS metadata exists on the target host, not necessarily on the CI agent.
# shellcheck source=/dev/null
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || {
  echo 'This setup targets Ubuntu 24.04 only.' >&2; exit 1;
}
[[ "$(dpkg --print-architecture)" == amd64 ]] || {
  echo 'The course images and validation tools require amd64.' >&2; exit 1;
}
apt-get update
apt-get install -y ca-certificates curl git python3 python3-venv shellcheck
install -d -m 0755 /etc/apt/keyrings
curl --fail --silent --show-error --location https://download.docker.com/linux/ubuntu/gpg \
  --output /etc/apt/keyrings/docker.asc
chmod 0644 /etc/apt/keyrings/docker.asc
cat > /etc/apt/sources.list.d/docker.sources <<'REPO'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
REPO
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker version
docker compose version
python3 --version
shellcheck --version
echo 'Builder tools installed. No user group memberships were changed.'
