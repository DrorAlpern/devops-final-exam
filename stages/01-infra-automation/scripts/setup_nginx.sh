#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/provisioning.log"
mkdir -p "$PROJECT_ROOT/logs"
touch "$LOG_FILE"

log() {
    printf '%s - BASH - %s - %s\n' "$(date -Iseconds)" "$1" "$2" | tee -a "$LOG_FILE"
}
on_error() {
    local status="$1"
    local line="$2"
    log ERROR "Setup failed on line $line (exit $status)."
    exit "$status"
}
trap 'on_error "$?" "$LINENO"' ERR

run_logged() {
    "$@" >>"$LOG_FILE" 2>&1
}

fail() {
    log ERROR "$1"
    exit 1
}

log INFO "Nginx setup started."
[[ "$(uname -s)" == "Linux" ]] || fail "This script requires Linux."
[[ -r /etc/os-release ]] || fail "Cannot identify the Linux distribution."
# shellcheck source=/dev/null
source /etc/os-release
[[ "$ID" == "ubuntu" || "$ID" == "debian" ]] || fail "This script supports Ubuntu and Debian."
command -v systemctl >/dev/null || fail "systemd is required."
command -v curl >/dev/null || fail "curl is required for the HTTP health check."

ADMIN=()
if (( EUID != 0 )); then
    command -v sudo >/dev/null || fail "sudo is required."
    sudo -n true 2>/dev/null || fail "Run 'sudo -v' before starting the simulator."
    ADMIN=(sudo -n)
fi

if dpkg-query -W -f='${Status}' nginx 2>/dev/null | grep -q '^install ok installed$'; then
    log INFO "Nginx is already installed; skipping package installation."
else
    log INFO "Installing Nginx. Package output is written to provisioning.log."
    run_logged "${ADMIN[@]}" env DEBIAN_FRONTEND=noninteractive apt-get update
    run_logged "${ADMIN[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
    log INFO "Nginx package installed."
fi

install_if_changed() {
    if ! cmp -s "$1" "$2"; then
        "${ADMIN[@]}" install -m 0644 "$1" "$2"
        log INFO "Updated $2."
    fi
}

"${ADMIN[@]}" install -d -m 0755 /var/www/infra-automation
install_if_changed "$PROJECT_ROOT/configs/index.html" /var/www/infra-automation/index.html
install_if_changed "$PROJECT_ROOT/configs/nginx.conf" /etc/nginx/sites-available/infra-automation
if [[ "$(readlink /etc/nginx/sites-enabled/infra-automation || true)" != "/etc/nginx/sites-available/infra-automation" ]]; then
    "${ADMIN[@]}" ln -sfn /etc/nginx/sites-available/infra-automation /etc/nginx/sites-enabled/infra-automation
fi

run_logged "${ADMIN[@]}" /usr/sbin/nginx -t
run_logged "${ADMIN[@]}" systemctl enable --now nginx
run_logged "${ADMIN[@]}" systemctl reload nginx
"${ADMIN[@]}" systemctl is-active --quiet nginx
curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 1 --max-time 10 http://127.0.0.1:8080/ >/dev/null
log INFO "Nginx setup completed. Demo site: http://127.0.0.1:8080"
