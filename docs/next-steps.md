# Delivery status

The public `main` branch is the reviewer entry point. It contains the rolling
project, including Stage 1, and links to the separate Docker/Kubernetes module
assignment. No course submission is sent by project scripts.

Completed release checks are recorded in
[local submission evidence](evidence/local-submission.md): fresh public clone,
Compose startup, Terraform apply and no-change plan, actual kind workloads,
Helm recovery exercises, Jenkins build, scans, and Docker Hub publication.

To review or demonstrate the project, follow [the local guide](../lab/README.md).
It does not require a cloud account. After reviewing the documentation and
running the demonstration, the public repository link is the handoff artifact.

The course permits an equivalent network and kind. This implementation uses
Moto for AWS API emulation and labels that boundary in the application and
submission guide. A real AWS deployment has not been performed. The cloud
configuration remains available under `terraform` and would require its own
account, plan, apply, SSH, IAM, and browser checks.
