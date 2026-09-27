# Requirements and implementation

The rolling project follows the supplied end-to-end brief. Subsequent course
guidance states that dedicated infrastructure is no longer available, an
equivalent network may be used, kind is acceptable, and public GitHub source
is the review artifact. Docker/Kubernetes is a separate module assignment.

| Requirement | Location | Demonstration |
| --- | --- | --- |
| Stage 1 automation | stages/01-infra-automation | Python machine simulation and Bash/Nginx setup |
| Git branches | feature branches, dev, main | Reviewed development and final pull request |
| Infrastructure as code | terraform; lab/terraform | Cloud configuration accepts an existing VPC; local profile applies against Moto |
| Docker and debugging | app; tests/test_app.py | Multi-stage build; VPC, ELB, and owned-AMI queries; pagination and error handling |
| Jenkins | Jenkinsfile; ci/jenkins | Real local controller/agent pipeline and Docker Hub publication |
| Kubernetes files | lab/k8s; k8s | Actual kind workloads; raw manifests committed |
| Helm | helm/flask-aws-monitor | Configurable image, environment, replicas, resources, Service, and optional Ingress |
| Documentation | README files; docs | Reproduction commands, limitations, and dated evidence |

## Local environment boundary

The actual compute is the Linux development VM and its containers. Moto stores
AWS-shaped resource records and answers API requests; it does not boot EC2
machines or prove cloud permissions. The app visibly identifies this mode.
Cloud-only checks are not represented as completed by local tests.

The original AWS configuration remains under `terraform`. Its VPC is now
an input instead of the retired course VPC. Private keys are generated outside
Terraform, and only the public key is passed to the provider. No private key
contents are stored by the configuration.

## Optional work

The Azure pipeline is provided but was not executed. Ingress was exercised
locally over HTTP; HTTPS was not demonstrated. Terraform remote-exec is not
implemented. These are not described as passed bonus items.

## Source material

- [End-to-end brief](https://docs.google.com/document/d/15LF99pO3h7yz7pXHeyrR9aejvMt3GbZ1ny64zZby6aA/edit)
- [Jenkins slides linked by the brief](https://docs.google.com/presentation/d/1IteHsyHaXBItZaUJ5OIEM74Iyaxhpw0W9__AY6fSOg4/edit)
