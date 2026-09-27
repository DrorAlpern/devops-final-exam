"""Check the real application against local Moto resources and their lifecycle."""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from urllib.request import urlopen

import boto3


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def page(path):
    # Fixed local service; no user-controlled URL or protocol.
    with urlopen("http://127.0.0.1:5001" + path, timeout=20) as response:  # nosec B310
        check(response.status == 200, f"Unexpected HTTP status: {response.status}")
        return response.read().decode()


def main():
    check(os.getenv("AWS_ENDPOINT_URL") == "http://moto:5000", "Local Moto endpoint required")
    check(os.getenv("AWS_ACCESS_KEY_ID") == "local-lab", "Dummy credentials required")
    session = boto3.Session(region_name="us-east-1")
    ec2, elb = session.client("ec2"), session.client("elbv2")
    instances = [
        instance
        for reservation in ec2.describe_instances()["Reservations"]
        for instance in reservation["Instances"]
        if instance["State"]["Name"] == "running"
    ]
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "tag:Name", "Values": ["devops-lab"]}])["Vpcs"]
    images = ec2.describe_images(Owners=["self"])["Images"]
    load_balancers = elb.describe_load_balancers()["LoadBalancers"]
    counts = dict(
        instances=len(instances),
        vpcs=len(vpcs),
        images=len(images),
        load_balancers=len(load_balancers),
    )
    check(all(counts.values()), f"Missing Terraform resources: {counts}")
    html = page("/")
    check("Local AWS API lab" in html, "The emulator notice is missing")
    check("local-monitor-alb" in html and "local-builder-image" in html, "Inventory missing")
    for resource in [instances[0]["InstanceId"], vpcs[0]["VpcId"], images[0]["ImageId"]]:
        check(resource in html, f"API resource missing from HTML: {resource}")
    check(json.loads(page("/healthz")) == {"status": "ok"}, "Health check failed")
    name = "lifecycle-check-" + uuid.uuid4().hex[:10]
    image_id = ec2.register_image(Name=name)["ImageId"]
    try:
        check(name in page("/"), "New API resource did not appear in the application")
    finally:
        ec2.deregister_image(ImageId=image_id)
    check(name not in page("/"), "Deleted API resource remains in the application")
    print(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": "Moto AWS API emulation",
                "counts": counts,
                "health": 200,
                "inventory": 200,
                "image_create_delete": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Local verification failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
