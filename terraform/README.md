# AWS infrastructure

This is the real AWS deployment option. For the account-free submission,
use [the local lab](../lab/README.md), which provisions an equivalent network
against Moto and runs the application in Docker or kind.

This configuration creates one Ubuntu 24.04 EC2 instance named `builder` in
`us-east-1`. Supply an existing VPC and public subnet through `vpc_id` and
`subnet_id`. The original course network is no longer required. Incoming
TCP ports 22 and 5001 are restricted to the student's IPv4 CIDR; the root
volume is encrypted and IMDSv2 is required.

## Validate without an AWS account

From the repository root, install the development requirements and tools,
then run:

```bash
bash ci/check-terraform.sh
```

The script checks formatting, initializes the locked AWS provider, validates
the configuration, and runs ten mocked plan tests. Tests cover inbound port
restrictions, encryption, IMDSv2, key handling, and rejection of invalid
inputs or a subnet outside the selected VPC. Provider downloads require
Internet access; these tests make no AWS API requests.

The JUnit report is saved to ignored `reports/terraform-tests.xml` and
archived by Jenkins. These tests do not verify AWS permissions or capacity.

## Deploy to a real account

This option has not been executed. It requires an active AWS account and
can create chargeable resources. Authenticate using the normal AWS
credential chain; never put credentials in tracked files.

1. Run the [read-only network preflight](PREFLIGHT.md) with the intended
   account, VPC, and subnet.
2. In this directory, run `bash create-ssh-key.sh`. It refuses to overwrite
   an existing key and keeps the private key outside Git.
3. Copy `terraform.tfvars.example` to ignored `terraform.tfvars` and fill in
   the account, network, and permitted source IP.
4. Export the public key and review the plan:

```bash
export TF_VAR_ssh_public_key="$(cat ~/.ssh/devops-builder.pub)"
terraform init
terraform plan -out=builder.tfplan
```

After reviewing the resources and charges, apply that saved plan:

```bash
terraform apply builder.tfplan
ssh -i ~/.ssh/devops-builder ubuntu@"$(terraform output -raw public_ip)"
```

Terraform is restricted to the supplied account and checks subnet membership
in the selected VPC. Only the public key and private-key path enter the
configuration; the private key is never read into state. State, plans,
credentials, and actual variable files are excluded from Git.

The brief permits Docker installation through SSH. A real EC2 installation,
Jenkins execution there, and an HTTP check against that host remain untested.
The optional `remote-exec` bonus is not implemented. The verified local
execution is documented separately in [the submission guide](../docs/submission.md).

When finished with a real deployment, review `terraform plan -destroy` before
removing the resources managed by this configuration.
