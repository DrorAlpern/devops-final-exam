# CI pipelines

The root `Jenkinsfile` fixes the course starter's invalid parallel-stage
structure and replaces its placeholder commands with actual checks.

1. Check out the configured SCM branch.
2. Create a Python environment and install pinned validation tools.
3. Run linting, source/dependency checks, and a repository-wide secret scan in parallel.
4. Run Python tests, mocked Terraform plans, and deployment-file validation.
5. Build, scan, and smoke-test the image before publication.
6. Publish the commit tag and `latest` to `droralpern/flask-aws-monitor`.

Ruff, ShellCheck, Hadolint, and yamllint perform linting. Bandit and Trivy
perform security checks. The source scan fails on HIGH or CRITICAL findings;
a separate Trivy scan checks the entire public repository for secrets at any
severity. It skips only Git history and local/generated directories. There is
no blanket `ignore-unfixed` option. JSON reports and the Terraform JUnit XML
report are retained as build artifacts. Report paths are ignored by Git.

The image smoke test starts the exact image built by CI with no network or AWS
credentials. It checks that `/healthz` returns 200 and the inventory page
returns a helpful 503 without a traceback. The temporary container is removed
afterward, including when a check fails. This verifies application startup and
failure handling; a live AWS inventory still needs the course account.

## Jenkins setup

The course requires Jenkins on the AWS `builder` using its
[installation guide](https://docs.google.com/presentation/d/1IteHsyHaXBItZaUJ5OIEM74Iyaxhpw0W9__AY6fSOg4/edit).
The guide uses the `jenkins-workshop` branch of
[devopshift-welcome](https://github.com/yanivomc/devopshift-welcome).
That cloud installation has not been performed yet.

Before starting it, replace the sample administrator password and bind the
Jenkins UI to loopback for SSH access. The supplied Compose stack mounts the
Docker socket; run it only on the dedicated course builder with trusted
jobs. Do not expose the sample stack's default credentials on the Internet.
The required EC2 security group does not need a public Jenkins port.

The repeatable [local Jenkins lab](jenkins/README.md) runs a controller and a
separate agent labeled `docker`. The agent has Python 3.13 with venv support,
Git, ShellCheck, and Docker build access; the application image uses Python
3.12. The tool installer verifies pinned SHA256 checksums before installing
Hadolint, Trivy, Helm, kubeconform, and Terraform under `.tools/bin`.

The pipeline binds a **Secret file** credential with ID `dockerhub-config`.
It contains the Docker CLI login configuration, with permission to push to
`droralpern/flask-aws-monitor`. In the local lab, JCasC imports the VM's existing,
authorized Docker login through a read-only Compose secret. The pipeline
copies that bound file into a private temporary directory and removes the
copy after the push. Credential contents are never part of the repository.

The job uses **Pipeline from SCM**, branch `*/dev`, script `Jenkinsfile`.
Run every stage and retain the result, scan reports, and pushed image digest.
The cloud builder still needs its own installation and execution evidence.

## Azure DevOps

`azure-pipelines.yml` provides the equivalent jobs. Lint and Security have no
dependencies and can run in parallel; BuildAndPush waits for both. Configure a
Docker Registry service connection named `dockerhub`, limited to this
pipeline, using a Docker Hub token. Credentials stay in the service connection.
Azure execution and service-connection setup are still pending.

## Run checks on the development VM

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python ci/install-tools.py
bash ci/check.sh lint
bash ci/check.sh security
bash ci/check.sh test
bash ci/check-terraform.sh
```

The image-scan script expects a Docker-enabled agent. On this development VM,
Docker uses sudo; use a separately saved image archive with Trivy if running
it without a CI agent. No group permissions are changed by these scripts.

The preflight unit tests and Terraform mock tests run without an AWS identity.
The live [AWS preflight](../terraform/PREFLIGHT.md) is a separate, manual read
check after course access arrives; CI does not attempt it.

## Future AWS builder setup

After the approved EC2 builder is available, inspect and run:

```bash
sudo bash ci/prepare-builder.sh
```

The script targets Ubuntu 24.04 amd64. It installs Docker and Compose from the
[official Docker apt repository](https://docs.docker.com/engine/install/ubuntu/),
plus Git, Python with venv support, and ShellCheck. It enables Docker without
changing user group memberships. Only syntax and static analysis have been
checked here; an actual EC2 installation remains pending.
