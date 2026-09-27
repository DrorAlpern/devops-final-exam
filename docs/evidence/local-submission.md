# Local submission verification

Date: 27 September 2026. Host: Ubuntu 24.04, Linux amd64, 2 vCPU and 4 GiB RAM.
Jenkins, Compose, and kind are exercised in separate sessions on this host.

## Compose and Terraform

- `bash lab/run.sh up` built and started the actual Flask/Gunicorn image.
- Terraform applied 12 resources through AWS provider 6.64.0 to Moto 5.2.3.
- A subsequent plan reported no changes.
- API checks found the managed VPC, running instance record, owned AMI, and
  load-balancer record. HTTP health and inventory responses were both 200.
- Creating an AMI through the API made it appear in the application; deleting
  it removed it. No static inventory or Python response stubs were used.
- The published localhost port returned HTTP 200 from the host network.
- The desktop browser displayed all four resource tables and the visible
  emulation notice. Moto also supplies a default VPC, so the page can show
  two VPCs while the check counts one Terraform-managed VPC.
- A fresh emulator instance was reconciled successfully from saved state.

## Kubernetes and Helm

An isolated kind 0.33.0 cluster ran Kubernetes 1.35.8. The committed YAML
created the namespace, Moto Deployment/Service, Terraform Job/PVC, and
application Deployment/Service. The Terraform Job used the same configuration
and provider lock as Compose.

- Terraform completed successfully and a second Job applied with no changes.
- Raw-manifest and Helm deployments returned HTTP 200 and passed the same
  live API inventory/lifecycle checks.
- Deleting the raw application pod resulted in a new pod UID, readiness,
  and a successful inventory check.
- Helm upgraded the application to two ready replicas, then rolled back
  to one ready replica. Inventory checks passed after both operations.

The dedicated test cluster was created alongside an existing lab. This
required temporarily raising the host's inotify instance limit from 128 to
256; no deployment in the existing cluster was scaled down. The setup guide
links to kind's documented host-limit diagnosis. The project scripts do not
change kernel settings.

## Source and configuration checks

- 24 Python tests: inventory/pagination/error handling and network preflight.
- 10 preserved Stage 1 tests: validation, CLI, JSON output, and service failures.
- 10 mocked Terraform plan tests for the real AWS configuration.
- Ruff, ShellCheck, Hadolint, yamllint, and Bandit passed.
- Trivy source/dependency and repository-secret checks passed.
- Helm lint and schema validation passed for 16 Kubernetes resources.
- Invalid Helm replica counts and an Ingress without a hostname were rejected.

These are dated results, not a guarantee against future vulnerabilities.
Earlier Jenkins/image results are linked from [the evidence index](README.md).

## Scope of the evidence

The application, containers, Terraform/provider requests, and Kubernetes
workloads ran for real. AWS resources were API records in Moto. No EC2 VM
was booted, no AWS account was accessed, and no cloud networking or IAM
enforcement was validated. The separate real-AWS Terraform configuration
has validation and mocked tests but has not been applied to AWS.

## Jenkins and registry publication

[Jenkins build 6](jenkins-local-submission.json) completed successfully from
commit `328e0bbe206cfa6a1fe130576ef0eeea27252897`. Every stage passed, including
source checks, all 34 Python tests, ten mocked Terraform plans, deployment
validation, image build, image scan, isolated smoke test, and Docker Hub push.
The recorded source, image, Bandit, and secret scans contained no findings
at their configured thresholds.

Published image: `droralpern/flask-aws-monitor:328e0bbe206c` and `latest`.
Digest: `sha256:6c31d9a2113a88a6149453d35f5c485eb9ad8869de41388a7caa7e9bb1ce2c9e`.

## Fresh public clone

An independent clone of the public `dev` branch at `0ed6a11` was used after
removing the previous Compose containers and Terraform state volume. The
clone contained no virtual environment, tools folder, or private files.
`bash lab/run.sh up` initialized the pinned provider, created all 12 emulated
resources, built the image, and passed API lifecycle and published-port
checks. `bash lab/run.sh plan` then reported no changes. Existing host Docker
image caches were available; project state and source were fresh.

The cleanup command was also checked to remove its profiled Terraform volume
and download network. The temporary kind cluster was removed after testing,
and the host inotify setting was restored to its original value of 128.
