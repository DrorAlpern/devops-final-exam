# DevOps Rolling Project

This project packages a Flask AWS inventory application with Docker, builds it
through Jenkins, and deploys it with Kubernetes and Helm. Terraform defines the
builder infrastructure. Stage 1 contains the Python and Bash automation exercise.

## Run locally

Requirements: Linux amd64, Git, Docker Engine, and Docker Compose.

```bash
git clone https://github.com/DrorAlpern/devops-final-exam.git
cd devops-final-exam
bash lab/run.sh up
```

Open **http://127.0.0.1:15005** on the Docker host. For a remote host and the
Kubernetes run, see [lab/README.md](lab/README.md).

The local setup uses **Moto to simulate AWS APIs**. Terraform creates resource
records, and the application reads them through Boto3. Docker and Kubernetes
run the application itself. No EC2 machine is started in AWS. This distinction
is also shown on the page; the brief allows clearly marked mock implementations.

## Files

| Folder | Contents |
| --- | --- |
| [stages/01-infra-automation](stages/01-infra-automation/README.md) | Machine input, JSON validation, logging, and Bash/Nginx setup |
| [terraform](terraform/README.md) | AWS builder, SSH key reference, security group, and outputs |
| [app](app/README.md) | Flask application, dependencies, and multi-stage Dockerfile |
| [ci](ci/README.md) | Jenkins setup and check scripts; Jenkinsfile is at the root |
| [k8s](k8s/README.md) | Application Deployment and Service for AWS credentials |
| [helm](helm/README.md) | Application chart, configurable replicas and environment |
| [lab](lab/README.md) | Local Compose and kind setup with Moto |
| [docs](docs/README.md) | Architecture and execution results |

Stage 2 was previously assessed separately. The other assignment is
[Docker and Kubernetes: Crypto Price Tracker](https://github.com/DrorAlpern/docker-kubernetes-exam).

## Checks and versions

[Verification notes](docs/verification.md) identify the tested environments and
remaining cloud-only steps. The application image is published to
[Docker Hub](https://hub.docker.com/r/droralpern/flask-aws-monitor).

Work goes through feature branches, then `dev`, then a pull request into `main`.
The `stage-3-docker-starter` tag preserves the original missing-query error.

The Azure pipeline and chart's optional Ingress template correspond to bonus
items in the brief. Azure execution and Terraform remote-exec are not completed.
