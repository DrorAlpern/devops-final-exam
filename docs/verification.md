# Stage 3 verification

Recorded on 15 September 2026.

## Development environment

Ubuntu 24.04 development VM. Docker Engine 29.8.1, Compose 5.5.1, and
Terraform 1.16.2 were installed from the official Docker and HashiCorp apt
repositories. Docker remains accessible through sudo.

The official `hello-world` container ran successfully and was removed after
it exited. The application has since been built and run locally; no cloud resource has been deployed.

## Terraform configuration

- `terraform fmt -check`: passed.
- `terraform init -backend=false -input=false`: passed.
- AWS provider 6.64.0 selected and recorded in `.terraform.lock.hcl`.
- `terraform validate`: passed.
- SSH helper Bash syntax and ShellCheck: passed.
- Temporary SSH key check: public key generated, private file mode 0600,
  and a second run refused to overwrite the key.

## Not yet verified

- AWS account, required VPC, public subnet, and source-IP access.
- Terraform plan/apply and SSH into the EC2 builder.
- Jenkins and Docker Hub push.
- Kubernetes and Helm deployment.
- Azure DevOps bonus pipeline.

Configuration validation does not prove that AWS deployment will succeed.

## Docker starter checkpoint

- Python dependencies installed and their versions locked.
- Compose configuration validation passed.
- Multi-stage Docker image `flask-aws-monitor:starter` built successfully.
- The expected missing-`vpcs` NameError was reproduced with an EC2 stub,
  both on the host and inside the built image.
- Container UID 10001 and disabled Flask debug mode on import were verified.
- The original starter source is intentionally preserved in this checkpoint.
- EC2 deployment and a browser check against real AWS remain pending.

## Corrected application

- Seven application tests passed on the VM and inside the built container.
- Ruff and Bandit passed. Docker Compose configuration validation passed.
- Container HTTP checks: `/healthz` returned 200; the inventory returned a
  readable 503 without AWS credentials, with no traceback in the response.
- UID 10001, a read-only root filesystem, and a writable temporary directory
  were verified in the running container.
- Sample-data preview checked in a desktop browser and at a 390-pixel width.
  The narrow EC2 table scrolls horizontally without breaking resource values.
- These tests use stubs/sample data. They are not live AWS verification.

## CI scripts and image security

- Ruff, ShellCheck, Hadolint, and yamllint passed.
- Bandit and the Trivy source/dependency scan passed.
- The initial Debian image failed Trivy's HIGH/CRITICAL security gate.
  It was replaced by the official Python 3.12 Alpine image, with a pinned
  `libuuid` security update. No vulnerability-ignore rule was added.
- Final image scan: zero HIGH/CRITICAL findings with Trivy 0.74.0 and the
  downloaded vulnerability database on this date. This is a dated scan, not
  a guarantee against future findings.
- The seven application tests passed inside the Alpine image. Final image
  HTTP checks passed: health 200, missing-credentials inventory 503, CSS 200,
  and the Docker health-check command succeeded.
- Jenkins and Azure pipeline definitions are prepared. Their scripts were
  checked locally; Jenkins declarative validation and actual CI jobs remain
  pending. Docker Hub publication is separate from a successful CI run.
