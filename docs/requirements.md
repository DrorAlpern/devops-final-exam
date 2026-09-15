# Stage 3 requirements

Reviewed on 15 September 2026. The student confirmed that this exam outline is
the correct Stage 3 material. Final submission happens after the entire
rolling project is finished.

## Required work

| Section | Deliverable | Verification |
| --- | --- | --- |
| Git | New public repository; main, dev, and feature branches | Inspect branches, merges, and the final pull request |
| Terraform | EC2 named builder in us-east-1, in the course VPC | Plan/apply, SSH access, instance and security-group outputs |
| Docker | Multi-stage image, requirements, environment credentials, port 5001 | Build and run on the builder |
| Debugging | Fix missing VPC, load-balancer, and AMI queries | Tests and browser display of real AWS data |
| Jenkins | Parallel lint/security checks, image build and Docker Hub push | Successful job log and registry image |
| Azure DevOps | Equivalent pipeline, with secret credentials | Bonus; needs an Azure DevOps project and service connection |
| Kubernetes | Deployment and Service on the remote cluster | Ready pods, Service, and browser check |
| Helm | Configurable image, replicas, environment, resources, and Service | Lint, install, upgrade, and workload checks |
| Evidence | README in each source folder; logs or screenshots | Review actual results and clearly label incomplete work |

Ingress and automated Docker installation through Terraform remote-exec are
bonus tasks. The overview mentions Ingress as a deliverable, while its detailed
section marks it optional; include an optional chart template to support both.

## Dependencies to resolve

- Course AWS account and access method.
- Availability of the mandated VPC `vpc-044604d0bfb707142` in `us-east-1`, and a
  suitable public subnet. Do not silently create or substitute another VPC.
- Student source IP/CIDR for inbound ports 22 and 5001.
- Docker Hub: resolved. The `droralpern` account is connected and local Jenkins
  has successfully published through its secret-file credential.
- Remote Kubernetes cluster and access method.
- Existing Stage 2 code: not found in the two repositories visible under the
  connected GitHub account. Its absence does not remove the supplied starter
  application from the brief.

## Decisions based on the brief

1. Preserve the intentionally broken application in the Docker section's Git
   checkpoint, then fix it in the separate debugging feature branch.
2. Generate the SSH key outside Terraform. The example `tls_private_key`
   resource stores its private key in state, contradicting the written
   requirement. Terraform receives only the public key and outputs the local
   private-key path.
3. Use standard AWS credential environment variables or an available IAM role.
   Do not bake credentials into an image or commit them to the public repository.
4. Use real lint and security checks where the environment supports them.
   Any mock or unavailable integration must be explicitly identified.
5. The exam schedule in the source document does not establish a current
   deadline or prove that its temporary infrastructure is still available.

## Reference links

- [Course brief](https://docs.google.com/document/d/15LF99pO3h7yz7pXHeyrR9aejvMt3GbZ1ny64zZby6aA/edit)
- [Jenkins installation slides linked by the brief](https://docs.google.com/presentation/d/1IteHsyHaXBItZaUJ5OIEM74Iyaxhpw0W9__AY6fSOg4/edit#slide=id.g50771a00b0_0_1439)
- [HashiCorp explanation of private keys in state](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key)
