#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/bin:$PWD/.venv/bin:$PATH"
mkdir -p reports
case "${1:-}" in
  lint)
    ruff check app tests ci
    ruff format --check app tests ci
    find ci terraform -type f -name '*.sh' -print0 | xargs -0 shellcheck
    hadolint app/Dockerfile ci/jenkins/Controller.Dockerfile ci/jenkins/Agent.Dockerfile
    yamllint app/compose.yaml azure-pipelines.yml .yamllint.yml k8s ci/jenkins/*.yaml \
      helm/flask-aws-monitor/Chart.yaml helm/flask-aws-monitor/values.yaml
    ;;
  security)
    bandit -r app ci -c pyproject.toml -f json -o reports/bandit.json
    trivy fs --no-progress --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 \
      --format json --output reports/source-security.json app
    ;;
  test)
    python -m unittest discover -s tests -p 'test_*.py' -v
    ;;
  *) echo 'Usage: ci/check.sh lint|security|test' >&2; exit 2 ;;
esac
