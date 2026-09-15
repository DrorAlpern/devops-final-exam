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

Configure an agent with label `docker`, Python 3.12 with venv support, Git,
ShellCheck, and Docker build access. Check those prerequisites on the actual
course agent; the supplied image is not assumed to have current Python.
The helper installs Hadolint 2.15.1, Trivy 0.74.0, Helm 4.3.0, and kubeconform
0.8.0 locally under `.tools/bin`, verifying pinned SHA256 checksums.

Create a Jenkins **Username with password** credential with ID `dockerhub`.
Use your Docker Hub username and a write-capable personal access token as the
password. Enter the token directly in Jenkins, not in source or chat.
The VM's interactive Docker login is separate from this CI credential.

Create a **Pipeline from SCM** job for this repository, branch `*/dev`, script
path `Jenkinsfile`. Run it and preserve the stage result, build log, and pushed
image digest. The job must complete the actual push; local script checks do
not count as a successful Jenkins run.

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
