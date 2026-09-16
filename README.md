# DevOps Practical Project

A Flask dashboard for AWS inventory, packaged with Docker and supported by
Terraform, CI pipelines, Kubernetes manifests, and a Helm chart.
This repository implements the course outline supplied as Stage 3 of the
rolling project. Earlier stages remain separate.

**Work continues on `dev`.** The final merge to `main` and course submission
will happen after all required environments have been verified.

## Current status

| Component | Verified so far | Still required |
| --- | --- | --- |
| Flask application | Seven tests, container HTTP checks, sample-data browser preview | Live AWS inventory |
| Docker image | Built, scanned, and published to Docker Hub | Run on the EC2 builder |
| Terraform | Validation and ten mocked plan tests; preflight tool tested with stubs | Course account, plan, apply, SSH |
| Jenkins | Local controller/agent run, all stages passed, CI-driven Docker Hub push | Installation and run on the AWS builder |
| Azure DevOps | Equivalent pipeline prepared | Service connection and actual run |
| Kubernetes / Helm | Local rollout, recovery, scale-up/rollback, and Ingress routing/browser checks | Remote course deployment and live AWS inventory |

Published image: [droralpern/flask-aws-monitor](https://hub.docker.com/r/droralpern/flask-aws-monitor),
verified CI tag `47b6bf08a303`. No cloud resources have been
created. See [verification](docs/verification.md) for dated results and limits.

## Structure

| Directory | Purpose |
| --- | --- |
| [app](app/README.md) | Flask application, AWS policy reference, and Docker build |
| [terraform](terraform/README.md) | EC2 builder, security group, SSH key reference, and outputs |
| [ci](ci/README.md) | Local checks and support for Jenkins/Azure pipelines |
| [k8s](k8s/README.md) | Kubernetes Deployment and Service |
| [helm](helm/README.md) | Configurable application chart |
| [tests](tests/README.md) | Response-stub tests and a labeled sample-data preview |
| [docs](docs/README.md) | Requirements, explanations, and evidence |

## Local checks

Run these from the repository root on a Linux amd64 development machine
with Python 3.12 or 3.13, venv support, and ShellCheck:

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

The installer verifies pinned tool checksums and uses `.tools/bin`; it does
not change system permissions. Follow the app README to build and run Docker.
Without AWS credentials, the real inventory page returns a useful HTTP 503;
the test-only preview is explicitly labeled as sample data.

## Hands-on environments

- [Local Jenkins](ci/jenkins/README.md): run the pipeline and inspect its stages.
- [Local Kubernetes](ci/local-kubernetes/README.md): deploy, recover, scale, and roll back.
- [Local Ingress](ci/local-kubernetes/INGRESS.md): route two hostnames through Traefik.
- [Short practice session](docs/practice.md): follow the working system and explain it.

## Git workflow

The initial commit starts on `main`. Each section is developed on a
`feature/*` branch, checked, and merged into `dev`. The tag
`stage-3-docker-starter` preserves the intentionally broken course application
before its required debugging stage. Final delivery uses a pull request from
`dev` to `main`; later development commits are not pushed directly to `main`.

## Course material and notes

- [Course brief](https://docs.google.com/document/d/15LF99pO3h7yz7pXHeyrR9aejvMt3GbZ1ny64zZby6aA/edit)
- [Requirements and decisions](docs/requirements.md)
- [Project walkthrough](docs/walkthrough.md)
- [Remaining work](docs/next-steps.md)

All documentation is maintained in English. The application and pipeline
starter examples came from the course brief; their corrections are recorded
in Git. Local checks are not presented as completed cloud deployments.
