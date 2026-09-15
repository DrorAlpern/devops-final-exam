# CI pipelines

The root `Jenkinsfile` fixes the course starter's invalid parallel-stage
structure and replaces its placeholder commands with actual checks.

1. Check out the configured SCM branch.
2. Create a Python environment and install pinned validation tools.
3. Run linting and source/dependency security scans in parallel.
4. Run application tests, build the image, and scan the built image.
5. Publish the commit tag and `latest` to `droralpern/flask-aws-monitor`.

Ruff, ShellCheck, Hadolint, and yamllint perform linting. Bandit and Trivy
perform security checks. HIGH or CRITICAL Trivy findings fail the build;
there is no blanket `ignore-unfixed` option. JSON reports are retained as
build artifacts. Report paths are ignored by Git.

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
Hadolint, Trivy, Helm, and kubeconform under `.tools/bin`.

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
```

The image-scan script expects a Docker-enabled agent. On this development VM,
Docker uses sudo; use a separately saved image archive with Trivy if running
it without a CI agent. No group permissions are changed by these scripts.
