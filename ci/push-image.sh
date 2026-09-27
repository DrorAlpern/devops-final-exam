#!/usr/bin/env bash
set -euo pipefail
set +x
: "${DOCKERHUB_USERNAME:?Set the Docker Hub username}"
: "${DOCKER_CONFIG_FILE:?Bind the Docker login config from the CI credential store}"
: "${IMAGE_NAME:?Set IMAGE_NAME}"
: "${IMAGE_TAG:?Set IMAGE_TAG}"
[[ "$IMAGE_NAME" == "$DOCKERHUB_USERNAME/"* ]] || {
  echo 'The image namespace must match the authenticated username.' >&2
  exit 1
}
registry_config=$(mktemp -d "${TMPDIR:-/tmp}/monitor-registry.XXXXXX")
trap 'rm -rf -- "$registry_config"' EXIT
install -m 600 "$DOCKER_CONFIG_FILE" "$registry_config/config.json"
docker --config "$registry_config" push "$IMAGE_NAME:$IMAGE_TAG"
docker image tag "$IMAGE_NAME:$IMAGE_TAG" "$IMAGE_NAME:latest"
docker --config "$registry_config" push "$IMAGE_NAME:latest"
