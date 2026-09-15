# DevOps Practical Project

A course project that packages a Flask AWS resource monitor, provisions an
EC2 builder with Terraform, and adds CI/CD and Kubernetes deployments.

The course coordinator supplied the End-to-End DevOps Practical Exam Outline
as Stage 3 of the rolling project. Stage 1 remains in its existing repository.

## Current status

Requirements have been reviewed. Implementation and live verification are in
progress. The course AWS account, the required VPC, Docker Hub access, and the
remote Kubernetes cluster have not yet been verified. No cloud resources have
been created and no final submission has been sent.

## Structure

| Directory | Purpose |
| --- | --- |
| `terraform/` | EC2 builder, security group, SSH public key, and outputs |
| `app/` | Flask application and Docker build |
| `ci/` | Jenkins and Azure DevOps pipeline support |
| `k8s/` | Kubernetes Deployment and Service |
| `helm/` | Configurable application chart |
| `tests/` | Application tests and checks |
| `docs/` | Requirements, decisions, and verification evidence |

## Git workflow

The initial repository commit starts on `main`, as explicitly requested by the
brief. Create `dev` from it. Develop each section on its own `feature/*` branch,
validate it, and merge it into `dev`. The completed project goes from `dev` to
`main` through a pull request. Do not push later development commits directly
to `main`.

## Source material

- [Course brief](https://docs.google.com/document/d/15LF99pO3h7yz7pXHeyrR9aejvMt3GbZ1ny64zZby6aA/edit)
- [Requirements and open dependencies](docs/requirements.md)

All documentation is maintained in English. Starter application and pipeline
examples come from the course brief; corrections will be documented in Git.
