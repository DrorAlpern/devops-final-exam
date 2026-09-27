# Submission guide

## Deliverables

There are two assignments:

1. This repository is the rolling project. Stage 1 is included under
   [stages/01-infra-automation](../stages/01-infra-automation/README.md).
   The root application, infrastructure, and CI cover the later end-to-end work.
   Stage 2 was previously assessed separately.
2. [docker-kubernetes-exam](https://github.com/DrorAlpern/docker-kubernetes-exam)
   is the separate Docker/Kubernetes module assignment.

Both source repositories are public. This repository links to the second
assignment so that one entry link leads to both deliverables.

## Start with a fresh clone

Follow the root README, then run `bash lab/run.sh up`.
No secrets, private repository, or pre-existing cloud infrastructure are needed
for the local demonstration. First-run downloads need internet access.
Use `bash lab/kind.sh up` for the actual Kubernetes manifests and Helm chart.

Stage 1 has separate dependencies and installs Nginx when run; read its README
before running it. Its preserved tests can be run in an isolated Python venv.

## Environment selection

The updated course guidance permits an equivalent network and a kind cluster,
and requests public GitHub source for review. This implementation provides a
local API-emulation profile for reproducibility without a cloud account.
Kubernetes workloads and Jenkins run on the Linux development host.
Moto supplies simulated AWS resources; this is explicitly labeled in the UI.

The cloud Terraform configuration also accepts an equivalent existing VPC.
An EC2 deployment, real AWS IAM checks, and cloud network connectivity have
not been performed. The repository does not present local API emulation as
a completed AWS cloud deployment.

## Evidence and code

- [Local integration results](evidence/local-submission.md).
- [Earlier CI, image, Kubernetes, and security results](verification.md).
- [Architecture](architecture.md).
- [Requirements map](requirements.md).
- [Jenkins setup](../ci/jenkins/README.md) and root `Jenkinsfile`.
- [Local Kubernetes files](../lab/k8s/README.md) and [Helm chart](../helm/README.md).
- [Stage 1 verification](../stages/01-infra-automation/docs/verification.md).

Azure execution, Terraform remote-exec, and HTTPS are not demonstrated.
The optional local Ingress exercise is documented separately.
