# Stage 3 verification

Recorded on 15 September 2026.

## Development environment

Ubuntu 24.04 development VM. Docker Engine 29.8.1, Compose 5.5.1, and
Terraform 1.16.2 were installed from the official Docker and HashiCorp apt
repositories. Docker remains accessible through sudo.

The official `hello-world` container ran successfully and was removed after
it exited. No application container or cloud resource has been deployed yet.

## Terraform configuration

- `terraform fmt -check`: passed.
- `terraform init -backend=false -input=false`: passed.
- AWS provider 6.64.0 selected and recorded in `.terraform.lock.hcl`.
- `terraform validate`: passed.
- SSH helper Bash syntax and ShellCheck: passed.
- Temporary SSH key check: public key generated, private file mode 0600,
  and a second run refused to overwrite the key.

## Not yet verified

- AWS account, required VPC, public subnet, and source-IP access.
- Terraform plan/apply and SSH into the EC2 builder.
- Flask container build and application behavior.
- Jenkins and Docker Hub push.
- Kubernetes and Helm deployment.
- Azure DevOps bonus pipeline.

Configuration validation does not prove that AWS deployment will succeed.
