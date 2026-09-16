#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/bin:$PATH"
export TF_IN_AUTOMATION=1
mkdir -p reports
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform init -backend=false -input=false -lockfile=readonly -no-color
terraform -chdir=terraform validate -no-color
# This specific test file contains only mocked, plan-only runs.
terraform -chdir=terraform test -filter=tests/builder.tftest.hcl \
  -no-color -junit-xml=../reports/terraform-tests.xml
