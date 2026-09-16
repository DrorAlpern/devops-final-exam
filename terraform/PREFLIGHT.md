# Check the course AWS environment

Run this check **after receiving course access**, before a live Terraform plan.
It reads AWS data only. It does not create, update, or delete resources.
The required VPC is fixed to `vpc-044604d0bfb707142` in `us-east-1`.

## Run

From the repository root, install the development requirements if necessary:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Sign in using the course's approved method. Use the confirmed account and
subnet IDs in place of the placeholders below:

```bash
.venv/bin/python ci/aws_preflight.py \
  --account-id "COURSE_ACCOUNT_ID" \
  --subnet-id "COURSE_PUBLIC_SUBNET_ID"
```

If the login uses a named AWS profile, add `--profile course`. Otherwise,
Boto3 uses its standard credential chain, including environment credentials
or an instance role. Do not place credentials in commands, Git, or screenshots.
The standard AWS region is set explicitly by this script.

## What it checks

1. The current identity belongs to the expected account. A mismatch stops
   the check before any EC2 read requests.
2. The required course VPC exists and is available.
3. The subnet belongs to that VPC, is available, and has free IPv4 addresses.
4. Its effective route table has an active IPv4 default route to an Internet
   Gateway. An explicit subnet association takes precedence; otherwise the
   script reads the VPC's main route table. All response pages are read.
5. The Internet Gateway is attached to the course VPC.

A NAT Gateway, an IPv6-only route, or a blackhole route does not pass the
public IPv4 check. `MapPublicIpOnLaunch` does not need to be enabled because
the Terraform instance explicitly requests its own public IP.

Exit status `0` means these read checks passed; `1` means an AWS or environment
check failed; `2` means the command arguments were invalid. No partial run
prints a final success result. Raw AWS error details are not printed.

## Required read access

The script calls these APIs:

- STS: `GetCallerIdentity`.
- EC2: `DescribeVpcs`, `DescribeSubnets`, `DescribeRouteTables`, and
  `DescribeInternetGateways`.

Use the identity supplied by the course. This script neither grants IAM
permissions nor requires an administrator policy. Ask for the listed read
access if the course identity cannot inspect the network.

## What a pass does not prove

The check does not verify EC2 creation permissions, service quotas, instance
capacity, allowed source IP, network ACLs, SSH connectivity, or application
access. More-specific routes can also affect individual destinations.
A live Terraform plan and the approved deployment checks are still required.
No live AWS preflight has been performed yet.

The script is tested with Botocore Stubber. It covers successful explicit and
main routes, pagination, wrong accounts and VPCs, unavailable subnets,
invalid routes, detached gateways, input errors, and authentication failures.
Those tests run automatically without contacting AWS:

```bash
bash ci/check.sh test
```

References: [AWS route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
and [Boto3 credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).
