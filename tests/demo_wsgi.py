"""Local visual preview only. This file is not included in the production image."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import app as monitor  # noqa: E402

SAMPLE_DATA = {
    "instances": [
        {
            "id": "i-example-web",
            "state": "running",
            "type": "t3.medium",
            "public_ip": "203.0.113.10",
        },
        {"id": "i-example-worker", "state": "stopped", "type": "t3.micro", "public_ip": "N/A"},
    ],
    "vpcs": [{"id": "vpc-example", "cidr": "10.0.0.0/16"}],
    "load_balancers": [{"name": "example-web-alb", "dns": "web.example.com"}],
    "images": [{"id": "ami-example", "name": "example-ubuntu-base"}],
}
monitor.create_clients = lambda: (None, None)
monitor.fetch_resources = lambda *_: SAMPLE_DATA
app = monitor.app


@app.context_processor
def preview_context():
    return {"demo": True}
