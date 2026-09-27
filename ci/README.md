# CI pipeline

The root `Jenkinsfile` checks out the project, runs linting and security scans
in parallel, tests the code, builds the Docker image, scans it, and pushes it
to Docker Hub. It fixes the missing `parallel` block in the course starter.

Ruff, ShellCheck, Hadolint, and yamllint check the source files. Bandit and
Trivy perform the security scans. The image must also pass an HTTP smoke test
before publication. Reports are kept with the Jenkins build.

## Jenkins

Follow [jenkins/README.md](jenkins/README.md) to start the controller and its
Docker agent on the Linux host. The job reads `dev` and uses a Jenkins Secret
file named `dockerhub-config` for the registry login. Successful builds publish
a commit tag and `latest` to `droralpern/flask-aws-monitor`.

Jenkins was run locally. It was not installed on an AWS EC2 instance.

## Run the checks directly

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python ci/install-tools.py
bash ci/check.sh lint
bash ci/check.sh security
bash ci/check.sh test
bash ci/check-terraform.sh
bash ci/validate-deployment.sh
```

The tools target Linux amd64. ShellCheck must be installed on the host;
`install-tools.py` downloads the remaining pinned command-line tools and checks
their checksums. Image checks also need Docker access.

## Azure and builder setup

`azure-pipelines.yml` provides the brief's Azure pipeline bonus. It needs a
Docker Registry service connection named `dockerhub`; it has not been run.

`prepare-builder.sh` installs Docker and Compose on Ubuntu 24.04. It is kept
for the AWS configuration, with syntax/static checks only. The local host uses
sudo for Docker; the script does not change user group membership.
