"""Exercise AWS responses without contacting an AWS account."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import boto3
from botocore.exceptions import NoCredentialsError
from botocore.stub import Stubber

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import app as monitor  # noqa: E402


class InventoryTests(unittest.TestCase):
    def setUp(self):
        session = boto3.Session(
            aws_access_key_id="testing", aws_secret_access_key="testing", region_name="us-east-1"
        )
        self.ec2 = session.client("ec2")
        self.elb = session.client("elbv2")
        self.ec2_stub = Stubber(self.ec2)
        self.elb_stub = Stubber(self.elb)
        self.ec2_stub.activate()
        self.elb_stub.activate()
        self.addCleanup(self.ec2_stub.deactivate)
        self.addCleanup(self.elb_stub.deactivate)
        patcher = patch.object(monitor, "create_clients", return_value=(self.ec2, self.elb))
        self.clients = patcher.start()
        self.addCleanup(patcher.stop)
        monitor.app.testing = True
        self.client = monitor.app.test_client()

    def queue_empty(self):
        self.ec2_stub.add_response("describe_instances", {"Reservations": []}, {})
        self.ec2_stub.add_response("describe_vpcs", {"Vpcs": []}, {})
        self.elb_stub.add_response("describe_load_balancers", {"LoadBalancers": []}, {})
        self.ec2_stub.add_response("describe_images", {"Images": []}, {"Owners": ["self"]})

    def test_all_resource_types_and_pagination(self):
        first = {
            "InstanceId": "i-first",
            "InstanceType": "t3.micro",
            "State": {"Name": "running"},
            "PublicIpAddress": "203.0.113.10",
        }
        second = {
            "InstanceId": "i-second",
            "InstanceType": "t3.medium",
            "State": {"Name": "stopped"},
        }
        self.ec2_stub.add_response(
            "describe_instances",
            {"Reservations": [{"Instances": [first]}], "NextToken": "instances-2"},
            {},
        )
        self.ec2_stub.add_response(
            "describe_instances",
            {"Reservations": [{"Instances": [second]}]},
            {"NextToken": "instances-2"},
        )
        self.ec2_stub.add_response(
            "describe_vpcs", {"Vpcs": [{"VpcId": "vpc-example", "CidrBlock": "10.0.0.0/16"}]}, {}
        )
        self.elb_stub.add_response(
            "describe_load_balancers",
            {
                "LoadBalancers": [{"LoadBalancerName": "web-alb", "DNSName": "web.example.com"}],
                "NextMarker": "lb-2",
            },
            {},
        )
        self.elb_stub.add_response(
            "describe_load_balancers",
            {"LoadBalancers": [{"LoadBalancerName": "second-alb", "DNSName": "two.example.com"}]},
            {"Marker": "lb-2"},
        )
        self.ec2_stub.add_response(
            "describe_images",
            {"Images": [{"ImageId": "ami-first", "Name": "web-base"}], "NextToken": "images-2"},
            {"Owners": ["self"]},
        )
        self.ec2_stub.add_response(
            "describe_images",
            {"Images": [{"ImageId": "ami-second"}]},
            {"Owners": ["self"], "NextToken": "images-2"},
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        for value in [
            "i-first",
            "i-second",
            "vpc-example",
            "web-alb",
            "second-alb",
            "ami-first",
            "ami-second",
            "N/A",
        ]:
            self.assertIn(value, response.get_data(as_text=True))
        self.ec2_stub.assert_no_pending_responses()
        self.elb_stub.assert_no_pending_responses()

    def test_empty_inventory_is_a_successful_result(self):
        self.queue_empty()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True).count("No resources found in this category."), 4
        )

    def test_missing_credentials_returns_a_useful_503(self):
        self.clients.side_effect = NoCredentialsError()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertIn("Check the region, credentials, and read permissions", response.text)
        self.assertNotIn("Traceback", response.text)

    def test_permission_error_does_not_expose_provider_message(self):
        self.ec2_stub.add_client_error(
            "describe_instances",
            "UnauthorizedOperation",
            "PRIVATE_PROVIDER_MESSAGE",
            expected_params={},
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("PRIVATE_PROVIDER_MESSAGE", response.text)
        self.assertNotIn("No resources found", response.text)

    def test_partial_inventory_is_not_reported_as_complete(self):
        self.ec2_stub.add_response("describe_instances", {"Reservations": []}, {})
        self.ec2_stub.add_client_error(
            "describe_vpcs", "UnauthorizedOperation", "Denied", expected_params={}
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("View inventory", response.text)

    def test_resource_names_are_html_escaped(self):
        resources = {
            "instances": [],
            "vpcs": [],
            "load_balancers": [],
            "images": [{"id": "ami-example", "name": "<script>alert(1)</script>"}],
        }
        with patch.object(monitor, "fetch_resources", return_value=resources):
            response = self.client.get("/")
        self.assertIn("&lt;script&gt;", response.text)
        self.assertNotIn("<script>alert(1)</script>", response.text)

    def test_health_does_not_require_aws(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})
        self.clients.assert_not_called()


if __name__ == "__main__":
    unittest.main()
