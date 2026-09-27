# DevOps Rolling Project

A Flask dashboard for AWS inventory, with Terraform, a multi-stage Docker
image, Jenkins CI, Kubernetes manifests, and a Helm chart.

**Start here:** [Run the local lab](lab/README.md).
The complete local demonstration needs Docker and does not require an AWS
account. Terraform provisions API resources in Moto; the application reads
those resources through Boto3. Actual application containers run on Linux and
kind. The dashboard clearly identifies the emulated inventory.

## Review and run

```bash
git clone https://github.com/DrorAlpern/devops-final-exam.git
cd devops-final-exam
bash lab/run.sh up
```

Open **http://127.0.0.1:15005** on the Docker host. On a remote Linux host, use
the SSH tunnel described in [lab/README.md](lab/README.md).
The command also verifies all four resource categories and an API
create/delete operation. It downloads pinned tools/images on first use.

## Project map

| Path | Purpose |
| --- | --- |
| [stages/01-infra-automation](stages/01-infra-automation/README.md) | Stage 1: Python machine simulator and Bash/Nginx automation |
| [app](app/README.md) | Flask/Boto3 inventory dashboard and multi-stage Docker build |
| [lab](lab/README.md) | Reproducible Compose and kind environment using local AWS API emulation |
| [terraform](terraform/README.md) | Real-AWS deployment configuration with a configurable existing VPC |
| [ci](ci/README.md) | Quality gates, Jenkins controller/agent, and optional Azure pipeline |
| [k8s](k8s/README.md) | Raw Kubernetes manifests for a supplied AWS identity |
| [helm](helm/README.md) | Configurable application chart |
| [docs/submission.md](docs/submission.md) | Reviewer entry point, scope, and evidence |

The end-to-end application covers the later stages of the rolling project.
Stage 2 was previously assessed separately and is not recreated here.
The separate module assignment is
[Docker & Kubernetes: Crypto Price Tracker](https://github.com/DrorAlpern/docker-kubernetes-exam).

## Environment and evidence

- Jenkins builds, checks, scans, and publishes the application to
  [Docker Hub](https://hub.docker.com/r/droralpern/flask-aws-monitor).
- The local lab creates VPC, subnet, routing, EC2, AMI, and load-balancer API
  records in Moto, then checks the dashboard against those records.
- kind runs the actual application, emulator, and Terraform job. Helm manages
  a separate application release in that namespace.
- The real-AWS configuration remains available. Real EC2 provisioning, cloud
  IAM enforcement, and AWS network behavior have not been demonstrated.

See [current local verification](docs/evidence/local-submission.md) and
[earlier dated checks](docs/verification.md). Emulated EC2 records do not
represent booted virtual machines; the Linux host supplies the actual compute.

## Git workflow

Feature branches are reviewed and merged into `dev`; the delivery version
is merged into `main` through a pull request. The
`stage-3-docker-starter` tag preserves the original broken application
before the missing AWS resource queries were corrected.

All documentation is maintained in English. Source code, manifests, and
run instructions are public; credentials, state, and private logs are excluded.
