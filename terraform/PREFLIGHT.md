# Real AWS network preflight

This read-only helper checks a selected equivalent network in `us-east-1`.
Use it only for the real AWS deployment option. The [local lab](../lab/README.md)
has its own fixed emulator endpoint and does not require this check.

Install the development requirements, authenticate to your AWS account,
and substitute your actual IDs:

```bash
.venv/bin/python ci/aws_preflight.py \
  --account-id "YOUR_ACCOUNT_ID" \
  --vpc-id "YOUR_VPC_ID" \
  --subnet-id "YOUR_PUBLIC_SUBNET_ID"
```

For a named AWS profile, add `--profile your-profile`. Boto3 otherwise uses
its standard credential chain. Do not put credentials in Git or screenshots.

The helper checks:

1. The authenticated identity belongs to the expected account.
2. The selected VPC exists and is available.
3. The subnet belongs to that VPC and has free IPv4 addresses.
4. The effective route table has an active IPv4 default route to an Internet
   Gateway. Explicit subnet associations take priority over the main table.
5. That gateway is attached to the selected VPC.

All response pages are read. A NAT gateway, IPv6 route, or blackhole route
does not pass the public IPv4 check. Automatic public IP assignment need
not be enabled because Terraform explicitly requests a public IP.

Exit codes: `0` for success, `1` for an API/environment failure, `2` for
invalid arguments. Raw provider messages are not exposed. Required read
APIs are STS `GetCallerIdentity` and EC2 `DescribeVpcs`, `DescribeSubnets`,
`DescribeRouteTables`, and `DescribeInternetGateways`.

A pass does not prove creation permissions, quotas, instance capacity,
network ACL behavior, SSH access, or application availability. No live AWS
preflight has been performed. Fifteen stubbed tests exercise this helper
without AWS access as part of `bash ci/check.sh test`.
