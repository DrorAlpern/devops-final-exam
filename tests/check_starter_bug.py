"""Reproduce the supplied bug without making AWS API calls."""
import os
import sys
import unittest
from pathlib import Path

os.environ.update({
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_EC2_METADATA_DISABLED": "true",
})
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import app  # noqa: E402
from botocore.stub import Stubber  # noqa: E402


class StarterBugTest(unittest.TestCase):
    def test_missing_vpc_query_raises_name_error(self):
        app.app.testing = True
        with Stubber(app.ec2_client) as stub:
            stub.add_response("describe_instances", {"Reservations": []}, {})
            with self.assertRaisesRegex(NameError, "vpcs"):
                app.app.test_client().get("/")
            stub.assert_no_pending_responses()


if __name__ == "__main__":
    unittest.main()
