"""Check the course AWS account and public-subnet routing without changing resources."""

import argparse
import re

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

REGION = "us-east-1"
COURSE_VPC = "vpc-044604d0bfb707142"


class PreflightError(Exception):
    """A required account or network check did not pass."""


def require(condition, message):
    if not condition:
        raise PreflightError(message)


def route_tables(ec2, filters):
    pages = ec2.get_paginator("describe_route_tables").paginate(Filters=filters)
    return [table for page in pages for table in page["RouteTables"]]


def check_environment(sts, ec2, account_id, subnet_id):
    # Stop immediately if the current identity belongs to a different account.
    require(
        sts.get_caller_identity()["Account"] == account_id,
        "The active AWS identity does not match the expected course account.",
    )
    vpcs = ec2.describe_vpcs(VpcIds=[COURSE_VPC])["Vpcs"]
    require(
        len(vpcs) == 1 and vpcs[0].get("State") == "available",
        "The required course VPC is missing or unavailable in us-east-1.",
    )
    subnets = ec2.describe_subnets(SubnetIds=[subnet_id])["Subnets"]
    require(len(subnets) == 1, "The selected subnet was not found.")
    subnet = subnets[0]
    require(subnet.get("VpcId") == COURSE_VPC, "The subnet belongs to a different VPC.")
    require(subnet.get("State") == "available", "The selected subnet is not available.")
    require(subnet.get("AvailableIpAddressCount", 0) > 0, "The subnet has no free IPv4 addresses.")

    tables = route_tables(ec2, [{"Name": "association.subnet-id", "Values": [subnet_id]}])
    association = "explicit"
    if not tables:
        association = "main"
        tables = route_tables(
            ec2,
            [
                {"Name": "vpc-id", "Values": [COURSE_VPC]},
                {"Name": "association.main", "Values": ["true"]},
            ],
        )
    require(len(tables) == 1, "Could not identify exactly one effective route table.")
    table = tables[0]
    require(table.get("VpcId") == COURSE_VPC, "The route table belongs to a different VPC.")
    routes = [
        route
        for route in table.get("Routes", [])
        if route.get("DestinationCidrBlock") == "0.0.0.0/0"
        and route.get("State") == "active"
        and route.get("GatewayId", "").startswith("igw-")
    ]
    require(
        len(routes) == 1,
        "The effective route table needs an active IPv4 default route to an Internet Gateway.",
    )
    gateway_id = routes[0]["GatewayId"]
    gateways = ec2.describe_internet_gateways(InternetGatewayIds=[gateway_id])["InternetGateways"]
    require(
        len(gateways) == 1
        and any(
            attachment.get("VpcId") == COURSE_VPC and attachment.get("State") == "available"
            for attachment in gateways[0].get("Attachments", [])
        ),
        "The Internet Gateway is not attached to the required VPC.",
    )
    # MapPublicIpOnLaunch may be false: Terraform explicitly requests a public IP.
    return {
        "account": "The active identity matches the expected account.",
        "vpc": "The required course VPC is available in us-east-1.",
        "subnet": "The subnet belongs to the course VPC and has free IPv4 addresses.",
        "routing": f"The {association} route table has an active Internet Gateway default route.",
        "gateway": "The Internet Gateway is attached to the course VPC.",
    }


def account_value(value):
    if not re.fullmatch(r"[0-9]{12}", value):
        raise argparse.ArgumentTypeError("Use a 12-digit AWS account ID.")
    return value


def subnet_value(value):
    if not re.fullmatch(r"subnet-(?:[0-9a-f]{8}|[0-9a-f]{17})", value):
        raise argparse.ArgumentTypeError("Use a subnet ID containing 8 or 17 hexadecimal digits.")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account-id", required=True, type=account_value)
    parser.add_argument("--subnet-id", required=True, type=subnet_value)
    parser.add_argument(
        "--profile", help="optional existing AWS profile; otherwise use the default chain"
    )
    args = parser.parse_args(argv)
    try:
        session = boto3.Session(profile_name=args.profile, region_name=REGION)
        config = Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 2})
        checks = check_environment(
            session.client("sts", config=config),
            session.client("ec2", config=config),
            args.account_id,
            args.subnet_id,
        )
    except PreflightError as exc:
        print(f"FAIL: {exc}")
        return 1
    except NoCredentialsError:
        print("FAIL: No AWS credentials found. Sign in using the approved course login method.")
        return 1
    except ClientError:
        print("FAIL: AWS rejected a read request. Check login, read permissions, and resource IDs.")
        return 1
    except BotoCoreError:
        print("FAIL: Could not read AWS. Check the profile, credentials, and network connection.")
        return 1
    for label, message in checks.items():
        print(f"PASS [{label}]: {message}")
    print("No resources were changed. Write permissions, quotas, and connectivity remain untested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
