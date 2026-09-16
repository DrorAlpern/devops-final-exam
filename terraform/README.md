# AWS infrastructure

This configuration defines one Ubuntu 24.04 EC2 instance named `builder` in
`us-east-1`. It uses the existing course VPC `vpc-044604d0bfb707142`; it does not
create a VPC. Incoming TCP ports 22 and 5001 are restricted to the student's
IPv4 CIDR. The root volume is encrypted and IMDSv2 is required.

Status: formatting, provider initialization, configuration validation, and ten
mocked plan tests passed on the development VM. The SSH helper passed Bash
syntax, ShellCheck, and a temporary-key check. AWS access and the course VPC
have not been verified. No live AWS plan or apply has been run.

## Test without an AWS account

From the repository root:

```bash
.venv/bin/python ci/install-tools.py
bash ci/check-terraform.sh
```

The script checks formatting, initializes the locked provider without a
backend, validates the configuration, and runs `tests/builder.tftest.hcl`.
All ten runs use `mock_provider "aws"` and `command = plan`. They do not call
AWS or create resources. The first initialization may download the provider;
"offline" here means independent of an AWS account, not free of downloads.

Tests cover the restricted inbound ports, encryption, IMDSv2, outbound
access, and the private-key path without opening a key file. Invalid CIDRs,
account/subnet inputs, a private-key input, and a subnet in another VPC must
be rejected. A restricted /24 is accepted, while /32 remains preferred.
The JUnit report is written to ignored `reports/terraform-tests.xml` and
archived by Jenkins. Mocking does not verify AWS permissions or capacity.
See the [Terraform mocking documentation](https://developer.hashicorp.com/terraform/language/tests/mocking).

## Before applying

Obtain the course account and verify the mandated VPC. The selected subnet
must have a route to an Internet Gateway; a subnet ID alone does not prove it
is public. Confirm the instance size and charges before creating resources.

Run the [read-only environment preflight](PREFLIGHT.md) with the confirmed
account and subnet IDs before planning. Then review the real Terraform plan.

Authenticate using the course's supported AWS login method. Terraform uses
the standard AWS credential chain. Do not put AWS credentials in these files.

## SSH key and variables

Run from this directory on the machine that will manage the infrastructure:

```bash
bash create-ssh-key.sh
cp terraform.tfvars.example terraform.tfvars
```

Edit the ignored `terraform.tfvars` with the confirmed account, subnet, and
student source IP. Then make only the public key available to Terraform:

```bash
export TF_VAR_ssh_public_key="$(cat ~/.ssh/devops-builder.pub)"
```

The key-generation script refuses to overwrite an existing key. Keep the
private key outside the repository. Terraform stores the public key and the
private-key *path*; it never reads the private-key contents.

## Validate and provision

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=builder.tfplan
```

Review the plan before applying it. Applying creates chargeable AWS resources.
After the environment and plan have been approved:

```bash
terraform apply builder.tfplan
ssh -i ~/.ssh/devops-builder ubuntu@"$(terraform output -raw public_ip)"
```

The provider is restricted to the supplied course account, and a postcondition
rejects a subnet outside the required VPC. Commit `.terraform.lock.hcl` for
repeatable provider selection. State, saved plans, private keys, and real
variable files are excluded from Git.

## Docker installation and evidence

The brief allows manual installation through SSH. Docker installation on the
builder is a separate step, followed by version checks, image build, and an
HTTP check. These steps require a real instance and remain pending.

The optional Terraform `remote-exec` installation bonus is not implemented.
Do not report the VM or Docker deployment as complete based on validation
alone. Record successful apply, SSH, Docker, and HTTP results in the project
verification notes after performing them.

When the course no longer needs the instance, review `terraform plan -destroy`
and obtain approval before deleting the managed resources.
