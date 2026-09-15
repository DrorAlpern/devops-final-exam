"""Read-only AWS inventory for the DevOps course project."""

import os
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, render_template

app = Flask(__name__)
REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"


def create_clients():
    # Boto3 supports environment credentials, profiles, and instance roles.
    session = boto3.Session(region_name=REGION)
    config = Config(
        connect_timeout=3, read_timeout=10, retries={"mode": "standard", "max_attempts": 2}
    )
    return session.client("ec2", config=config), session.client("elbv2", config=config)


def items(client, operation, key, **parameters):
    for page in client.get_paginator(operation).paginate(**parameters):
        yield from page.get(key, [])


def fetch_resources(ec2, elb):
    instances = []
    for reservation in items(ec2, "describe_instances", "Reservations"):
        for instance in reservation.get("Instances", []):
            instances.append(
                {
                    "id": instance["InstanceId"],
                    "state": instance["State"]["Name"],
                    "type": instance["InstanceType"],
                    "public_ip": instance.get("PublicIpAddress", "N/A"),
                }
            )
    vpcs = [{"id": v["VpcId"], "cidr": v["CidrBlock"]} for v in items(ec2, "describe_vpcs", "Vpcs")]
    load_balancers = [
        {"name": lb["LoadBalancerName"], "dns": lb["DNSName"]}
        for lb in items(elb, "describe_load_balancers", "LoadBalancers")
    ]
    images = [
        {"id": image["ImageId"], "name": image.get("Name", "N/A")}
        for image in items(ec2, "describe_images", "Images", Owners=["self"])
    ]
    return {
        "instances": instances,
        "vpcs": vpcs,
        "load_balancers": load_balancers,
        "images": images,
    }


@app.get("/healthz")
def health():
    # This checks the web process, not AWS permissions or API availability.
    return {"status": "ok"}


@app.get("/")
def home():
    resources, error, status = None, None, 200
    try:
        resources = fetch_resources(*create_clients())
    except (BotoCoreError, ClientError) as failure:
        code = type(failure).__name__
        if isinstance(failure, ClientError):
            code = failure.response.get("Error", {}).get("Code", code)
        app.logger.warning("AWS inventory request failed: %s", code)
        error = (
            "AWS resources are unavailable. Check the region, credentials, and read permissions."
        )
        status = 503
    return render_template(
        "index.html",
        resources=resources,
        error=error,
        region=REGION,
        updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    ), status


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; base-uri 'self'; frame-ancestors 'none'"
    )
    return response
