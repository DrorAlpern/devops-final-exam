"""Verify AWS readiness decisions with queued API responses, never a live account."""

import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import boto3
from botocore.exceptions import NoCredentialsError, ProfileNotFound
from botocore.stub import Stubber

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
import aws_preflight as preflight  # noqa: E402

ACCOUNT = "123456789012"
SUBNET = "subnet-0123456789abcdef0"
GATEWAY = "igw-0123456789abcdef0"
ARGS = ["--account-id", ACCOUNT, "--subnet-id", SUBNET]
DEFAULT_ROUTE = {"DestinationCidrBlock": "0.0.0.0/0", "State": "active", "GatewayId": GATEWAY}


class PreflightTests(unittest.TestCase):
    def setUp(self):
        session = boto3.Session(
            aws_access_key_id="testing", aws_secret_access_key="testing", region_name="us-east-1"
        )
        self.sts = session.client("sts")
        self.ec2 = session.client("ec2")
        self.sts_stub = Stubber(self.sts)
        self.ec2_stub = Stubber(self.ec2)
        self.sts_stub.activate()
        self.ec2_stub.activate()
        self.addCleanup(self.sts_stub.deactivate)
        self.addCleanup(self.ec2_stub.deactivate)

    def tearDown(self):
        self.sts_stub.assert_no_pending_responses()
        self.ec2_stub.assert_no_pending_responses()

    def identity(self, account=ACCOUNT):
        self.sts_stub.add_response(
            "get_caller_identity",
            {"Account": account, "Arn": f"arn:aws:iam::{account}:user/test-only", "UserId": "test"},
            {},
        )

    def network(self, **subnet_changes):
        self.identity()
        self.ec2_stub.add_response(
            "describe_vpcs",
            {"Vpcs": [{"VpcId": preflight.COURSE_VPC, "State": "available"}]},
            {"VpcIds": [preflight.COURSE_VPC]},
        )
        subnet = {
            "SubnetId": SUBNET,
            "VpcId": preflight.COURSE_VPC,
            "State": "available",
            "AvailableIpAddressCount": 100,
            "MapPublicIpOnLaunch": False,
        } | subnet_changes
        self.ec2_stub.add_response(
            "describe_subnets", {"Subnets": [subnet]}, {"SubnetIds": [SUBNET]}
        )

    def routing(self, route=None, main=False, paginated=False, **table_changes):
        params = {"Filters": [{"Name": "association.subnet-id", "Values": [SUBNET]}]}
        if main:
            self.ec2_stub.add_response("describe_route_tables", {"RouteTables": []}, params)
            params = {
                "Filters": [
                    {"Name": "vpc-id", "Values": [preflight.COURSE_VPC]},
                    {"Name": "association.main", "Values": ["true"]},
                ]
            }
        if paginated:
            self.ec2_stub.add_response(
                "describe_route_tables", {"RouteTables": [], "NextToken": "page-2"}, params
            )
            params = params | {"NextToken": "page-2"}
        table = {
            "VpcId": preflight.COURSE_VPC,
            "RouteTableId": "rtb-0123456789abcdef0",
            "Routes": [DEFAULT_ROUTE if route is None else route],
        } | table_changes
        self.ec2_stub.add_response("describe_route_tables", {"RouteTables": [table]}, params)

    def gateway(self, attachments=None):
        if attachments is None:
            attachments = [{"VpcId": preflight.COURSE_VPC, "State": "available"}]
        self.ec2_stub.add_response(
            "describe_internet_gateways",
            {"InternetGateways": [{"InternetGatewayId": GATEWAY, "Attachments": attachments}]},
            {"InternetGatewayIds": [GATEWAY]},
        )

    def check(self):
        return preflight.check_environment(self.sts, self.ec2, ACCOUNT, SUBNET)

    def run_cli(self, args=None, session_error=None):
        output = io.StringIO()
        with (
            patch.object(preflight.boto3, "Session") as session,
            contextlib.redirect_stdout(output),
        ):
            session.side_effect = session_error
            session.return_value.client.side_effect = lambda name, **_: {
                "sts": self.sts,
                "ec2": self.ec2,
            }[name]
            code = preflight.main(ARGS if args is None else args)
        return code, output.getvalue(), session

    def test_explicit_public_route_does_not_require_auto_public_ip(self):
        self.network()
        self.routing()
        self.gateway()
        checks = self.check()
        self.assertEqual(len(checks), 5)
        self.assertIn("explicit", checks["routing"])

    def test_main_route_fallback_reads_all_pages(self):
        self.network()
        self.routing(main=True, paginated=True)
        self.gateway()
        self.assertIn("main", self.check()["routing"])

    def test_wrong_account_stops_before_ec2(self):
        self.identity(account="999999999999")
        with self.assertRaisesRegex(preflight.PreflightError, "expected course account"):
            self.check()

    def test_missing_or_unavailable_vpc_stops_before_subnet(self):
        for vpcs in [[], [{"VpcId": preflight.COURSE_VPC, "State": "pending"}]]:
            with self.subTest(vpcs=vpcs):
                self.identity()
                self.ec2_stub.add_response(
                    "describe_vpcs", {"Vpcs": vpcs}, {"VpcIds": [preflight.COURSE_VPC]}
                )
                with self.assertRaisesRegex(preflight.PreflightError, "missing or unavailable"):
                    self.check()

    def test_subnet_in_other_vpc_is_rejected(self):
        self.network(VpcId="vpc-0123456789abcdef0")
        with self.assertRaisesRegex(preflight.PreflightError, "different VPC"):
            self.check()

    def test_unavailable_or_full_subnet_is_rejected(self):
        for changes in [{"State": "pending"}, {"AvailableIpAddressCount": 0}]:
            with self.subTest(changes=changes):
                self.network(**changes)
                with self.assertRaises(preflight.PreflightError):
                    self.check()

    def test_nat_blackhole_and_ipv6_routes_do_not_prove_public_ipv4(self):
        routes = [
            {"DestinationCidrBlock": "0.0.0.0/0", "State": "active", "NatGatewayId": "nat-test"},
            DEFAULT_ROUTE | {"State": "blackhole"},
            {"DestinationIpv6CidrBlock": "::/0", "State": "active", "GatewayId": GATEWAY},
            {"DestinationCidrBlock": "10.0.0.0/16", "State": "active", "GatewayId": "local"},
        ]
        for route in routes:
            with self.subTest(route=route):
                self.network()
                self.routing(route=route)
                with self.assertRaisesRegex(preflight.PreflightError, "IPv4 default route"):
                    self.check()

    def test_missing_or_ambiguous_effective_route_table_is_rejected(self):
        for tables in [[], [{"VpcId": preflight.COURSE_VPC}] * 2]:
            with self.subTest(tables=tables):
                self.network()
                self.ec2_stub.add_response(
                    "describe_route_tables",
                    {"RouteTables": tables},
                    {"Filters": [{"Name": "association.subnet-id", "Values": [SUBNET]}]},
                )
                if not tables:
                    self.ec2_stub.add_response(
                        "describe_route_tables",
                        {"RouteTables": []},
                        {
                            "Filters": [
                                {"Name": "vpc-id", "Values": [preflight.COURSE_VPC]},
                                {"Name": "association.main", "Values": ["true"]},
                            ]
                        },
                    )
                with self.assertRaisesRegex(preflight.PreflightError, "exactly one"):
                    self.check()

    def test_route_table_in_other_vpc_is_rejected(self):
        self.network()
        self.routing(VpcId="vpc-0123456789abcdef0")
        with self.assertRaisesRegex(preflight.PreflightError, "route table belongs"):
            self.check()

    def test_missing_detached_or_wrong_vpc_gateway_is_rejected(self):
        for attachments in [
            [],
            [{"VpcId": preflight.COURSE_VPC, "State": "detaching"}],
            [{"VpcId": "vpc-0123456789abcdef0", "State": "available"}],
        ]:
            with self.subTest(attachments=attachments):
                self.network()
                self.routing()
                self.gateway(attachments)
                with self.assertRaisesRegex(preflight.PreflightError, "not attached"):
                    self.check()

    def test_aws_denial_exits_nonzero_without_raw_provider_message(self):
        self.identity()
        self.ec2_stub.add_client_error(
            "describe_vpcs",
            "UnauthorizedOperation",
            "PRIVATE_PROVIDER_MESSAGE",
            expected_params={"VpcIds": [preflight.COURSE_VPC]},
        )
        code, output, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("read permissions", output)
        self.assertNotIn("PRIVATE_PROVIDER_MESSAGE", output)
        self.assertNotIn("PASS", output)

    def test_missing_credentials_has_clear_nonzero_result(self):
        code, output, _ = self.run_cli(session_error=NoCredentialsError())
        self.assertEqual(code, 1)
        self.assertIn("No AWS credentials", output)

    def test_invalid_profile_does_not_print_traceback(self):
        code, output, _ = self.run_cli(session_error=ProfileNotFound(profile="private-profile"))
        self.assertEqual(code, 1)
        self.assertIn("Check the profile", output)
        self.assertNotIn("private-profile", output)
        self.assertNotIn("Traceback", output)

    def test_invalid_arguments_are_rejected_before_aws_session(self):
        for account, subnet in [("123", SUBNET), (ACCOUNT, "subnet-invalid")]:
            with self.subTest(account=account, subnet=subnet):
                with patch.object(preflight.boto3, "Session") as session:
                    with (
                        contextlib.redirect_stderr(io.StringIO()),
                        self.assertRaises(SystemExit) as e,
                    ):
                        preflight.main(["--account-id", account, "--subnet-id", subnet])
                    self.assertEqual(e.exception.code, 2)
                    session.assert_not_called()

    def test_cli_success_uses_selected_profile_and_fixed_course_region(self):
        self.network()
        self.routing()
        self.gateway()
        code, output, session = self.run_cli(ARGS + ["--profile", "course"])
        self.assertEqual(code, 0)
        session.assert_called_once_with(profile_name="course", region_name="us-east-1")
        self.assertEqual(output.count("PASS ["), 5)
        self.assertIn("No resources were changed", output)


if __name__ == "__main__":
    unittest.main()
