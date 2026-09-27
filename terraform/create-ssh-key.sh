#!/usr/bin/env bash
set -euo pipefail

key_path="${1:-${HOME}/.ssh/devops-builder}"
if [[ -e ${key_path} || -e ${key_path}.pub ]]; then
    echo "A key file already exists at ${key_path}; nothing was overwritten." >&2
    exit 1
fi

umask 077
mkdir -p "$(dirname "${key_path}")"
ssh-keygen -q -t ed25519 -N '' -C 'devops-course-builder' -f "${key_path}"
chmod 0600 "${key_path}"
echo "Private key: ${key_path}"
echo "Public key: ${key_path}.pub"
