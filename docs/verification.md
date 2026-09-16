# Stage 3 verification

Initial checks: 15 September 2026. Local CI and cluster checks: 16 September 2026.

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
- Jenkins installation and execution on the AWS builder.
- Kubernetes and Helm deployment on the remote course cluster.
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
- Jenkins passed declarative validation and completed a real local build
  with a Docker Hub push on 16 September. Azure execution remains pending.

## Docker Hub publication

- Published `droralpern/flask-aws-monitor:b07205ae146d` and `latest`.
- Registry digest: `sha256:29c91978e04b6ef6bf28aa77f40d994f36f836c998e6d7f722dad9854e69bb9e`.
- Registry inspection confirmed the digest and Linux amd64 platform.
- Publication was performed from the development VM, not through Jenkins.

## Kubernetes and Helm

- Helm 4.3.0 strict lint passed.
- kubeconform 0.8.0 validated eight resources with zero invalid, erroneous,
  or skipped resources, using Kubernetes 1.35.0 schemas.
- Checks cover raw manifests, chart defaults, and an override with three
  replicas, port 8080, LoadBalancer, Ingress, and adjusted memory limits.
- Invalid zero replicas and enabled Ingress without a host were rejected.
- The target cluster's version and architecture still need confirmation.
- Local Helm installation, upgrade, and rollback subsequently passed. Remote
  deployment and Ingress routing still need their target environments.

## Local Jenkins execution — 16 September 2026

Jenkins 2.568.3 runs in a container with no controller executors. A separate
inbound agent uses the `docker` label, Python 3.13, and Docker CLI 29.8.0.
Anonymous access and self-registration are disabled; the UI is loopback-only.

- The Jenkins declarative validator accepted the Jenkinsfile.
- Build #1 checked out `a56aa0c325f408ce704fde5634df686410ae33c9` from `dev`.
- Checkout, tool preparation, parallel lint/security, seven application tests,
  deployment validation, image build, image scan, and registry push succeeded.
- The image and source scans reported zero HIGH/CRITICAL vulnerabilities.
- Bandit, source scan, and image scan JSON reports were archived by Jenkins.
- Both the commit tag `a56aa0c325f4` and `latest` were pushed by the job.
- Published digest: `sha256:e286831bd4c58519c842c8149fea9c97a5aaad5a17c2f1e2e097faa37c4a9205`.

The credential came from the existing authorized Docker login and was bound
as a Jenkins secret file. The full logs and scan reports remain in the local
Jenkins volume. [Reviewed stage results](evidence/jenkins-local.json) contain
no credentials. This verifies local Jenkins; the course still requires the
installation and execution on its AWS builder.

## Local Kubernetes execution — 16 September 2026

kind 0.33.0 created a single-node Kubernetes 1.35.8 cluster. Its API listens
only on loopback. kubectl 1.35.8 and Helm 4.3.0 were used.

- Production manifests deployed successfully; the image was pulled from Docker Hub.
- Both the raw deployment and Helm release returned health 200 and inventory
  503 with intentionally empty local credentials.
- After deleting one raw-deployment pod, Kubernetes created a replacement
  with a different UID and restored readiness.
- Helm revision 1 used one replica and image tag `b07205ae146d`.
- Revision 2 changed to tag `a56aa0c325f4` and reached three ready replicas.
- Revision 3 rolled back to one ready replica and the previous image tag.
- A separate, explicitly labeled sample-data deployment was checked in the
  workstation browser through the Kubernetes Service and SSH tunnel.
- No real AWS credentials were supplied and no live AWS resources were queried.

[Reviewed cluster results](evidence/kubernetes-local.json) include the actual
Helm history. The scripts under `ci/local-kubernetes` reproduce this exercise.
The future Ubuntu builder setup script passed syntax/static checks; it has
not been run on an EC2 instance.

## Final local CI check — 16 September 2026

After the Kubernetes helpers were merged into `dev`, Jenkins build #2
completed every stage successfully against `daa038cd34f8d18f5c223ea405e5600b23ccbe0b`.
The repeatable Jenkins startup also preserved build #1 and its artifacts.
The job published tag `daa038cd34f8` and `latest`, with digest
`sha256:e072aa585d6bf0565ae17176d7525ac7bce55603f20b4b37bc592cacc2b169bc`.
Bandit, source security, and image security reports contained zero findings
at their configured thresholds. Full original logs and reports are retained
in Jenkins and in the ignored `evidence/private/jenkins-build-2` folder; the
[public stage summary](evidence/jenkins-local-latest.json) contains no secrets.

## Local Ingress execution — 16 September 2026

The official Traefik chart 41.5.0 was downloaded and checksum-verified. Its
Traefik 3.7.13 image is pinned by digest. Six rendered controller resources
and the sample preview Ingress passed strict Kubernetes schema validation.
The controller and both application routes deployed successfully in kind.

- Production hostname: health 200 and inventory 503 with the expected AWS
  access message. No sample data appeared on that route.
- Preview hostname: inventory 200, a visible sample-data notice, all four
  resource sections, and the expected application security header.
- The stylesheet returned 200 through the Ingress.
- An unconfigured hostname returned the controller's 404 response.
- Both hostnames were checked in the workstation browser through SSH.

[Recorded HTTP results](evidence/ingress-local.json) and the
[repeatable exercise](../ci/local-kubernetes/INGRESS.md) describe exactly what
was tested. The controller is available only through a local port forward;
no public endpoint or DNS record was created. HTTPS and remote Ingress
verification remain outside this local HTTP check.
