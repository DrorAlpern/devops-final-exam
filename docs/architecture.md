# Project architecture

```mermaid
flowchart LR
    git[GitHub] --> ci[Jenkins on Linux]
    ci --> checks[Lint, tests, security]
    checks --> image[Docker image]
    image --> hub[Docker Hub]
    hub --> app[Flask in kind]
    image --> compose[Flask in Compose]
    compose -->|Boto3 read requests| moto
    tf[Terraform local profile] --> moto[Moto AWS API emulator]
    app -->|Boto3 read requests| moto
    browser[Browser] --> app
    helm[Helm chart] --> app
```

GitHub stores source and history. Jenkins checks the source, builds and scans
the application image, and publishes a commit tag. Compose or kind runs the
application. Helm manages a separate release in kind.

Terraform creates VPC, subnet, routing, security-group, EC2, AMI, and
load-balancer records in Moto. The dashboard reads those records on every
request. Each page request reads the current API response.

The emulator's EC2 entry is a record, not a booted VM. The actual application
and Jenkins run on the Linux development host. A separate Terraform
configuration supports real AWS deployment into a supplied existing VPC,
but that cloud path has not been run.

## Credentials and access

The local profile uses fixed dummy credentials and local service endpoints.
Compose uses an internal API network, a localhost web port, and a separate
network for Terraform provider downloads.
The kind Services are internal; browser access uses loopback port forwarding.

Real AWS keys, Docker Hub tokens, Terraform state, and kubeconfig files are
excluded from public Git history. The Jenkins Docker-capable agent is used
only for trusted project code.
