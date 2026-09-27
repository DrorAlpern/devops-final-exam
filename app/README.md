# AWS Resource Monitor

The Flask app lists EC2 instances, VPCs, ELBv2 load balancers, and account-owned
AMIs in `us-east-1`. The starter used `vpcs`, `lbs`, and `amis` without fetching
them. The corrected version queries those resources and reads all response pages.
The original error is preserved in the `stage-3-docker-starter` Git tag.

## Run

For the tested local environment, follow [the lab guide](../lab/README.md).
To build the application alone from the repository root:

```bash
docker compose -f app/compose.yaml up -d --build
curl -f http://127.0.0.1:5001/healthz
```

The inventory page needs AWS credentials or the lab's Moto endpoint. Compose
passes AWS credential environment variables from the shell. If Docker needs
sudo, use `sudo --preserve-env=AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_SESSION_TOKEN`
before the Docker command so those exported values are available. `iam-read-policy.json`
lists the read permissions needed in AWS. Keep actual credentials outside Git.
An unavailable API produces HTTP 503; an empty successful query stays HTTP 200.
The health endpoint only checks the web process.

## Image and checks

The Dockerfile installs dependencies in its first stage and copies them into
a smaller runtime stage. Gunicorn serves port 5001 as a non-root user. The
runtime uses the pinned Python 3.12 Alpine image and a fixed `libuuid` package
version required by the security scan. Boto3 clients are reused within each
worker to avoid rebuilding their service models on every request.

Run `bash ci/check.sh test` from the root for application tests.
The local inventory is tested against Moto; the real AWS deployment is untested.
