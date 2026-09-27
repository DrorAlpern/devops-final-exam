# Verification

Test host: Ubuntu 24.04, Linux amd64. The local environment uses Moto for AWS
API responses and kind for Kubernetes. It does not verify real EC2 startup,
AWS network access, or IAM enforcement.

## Checks

| Command | What it checks |
| --- | --- |
| `bash ci/check.sh lint` | Python, shell, Dockerfile, and YAML syntax/style |
| `bash ci/check.sh security` | Python issues, dependency vulnerabilities, and accidental secrets |
| `bash ci/check.sh test` | Application responses and the Stage 1 simulator |
| `bash ci/check-terraform.sh` | Terraform validation and ten mocked plan tests |
| `bash ci/validate-deployment.sh` | Helm rendering and Kubernetes schemas |
| `bash lab/run.sh up` | Compose startup, Terraform apply, inventory, and published HTTP port |
| `bash lab/run.sh plan` | Repeat plan against the running emulator |
| `bash lab/kind.sh up` | Published application image, Terraform Job, raw manifests, and Helm |
| `bash lab/kind.sh verify` | Inventory, Helm replica change, and rollback |

On 27 September 2026, a fresh public clone started successfully with no project
state or private files. Terraform created 12 emulated resources, all four
inventory sections were populated, HTTP returned 200, and a second plan showed
no changes. The kind deployment and Helm upgrade/rollback also passed.

[Jenkins build 6](evidence/jenkins-local-submission.json) records the earlier
successful pipeline and image publication. Its test count includes the AWS
preflight helper that has since been removed. Current review results are in
[the evidence folder](evidence/README.md).

## Not executed

The real AWS configuration has validation and mocked tests only. The local
Linux VM runs Docker and Jenkins. Azure pipeline execution, Terraform
remote-exec, and HTTPS are not claimed as completed work.
