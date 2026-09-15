# AWS Resource Monitor

A Flask dashboard that lists EC2 instances, VPCs, ELBv2 load balancers, and
account-owned AMIs in `us-east-1`. It only reads AWS resources. Every listing
uses a paginator, so a response is not limited to the first API page.

## Build and run on the development VM

From the repository root:

```bash
sudo docker compose -f app/compose.yaml up -d --build
curl --fail http://127.0.0.1:5001/healthz
```

Open `http://127.0.0.1:5001` on that machine. From your own computer, forward
port 5001 over SSH, then open the same address locally:

```bash
ssh -N -L 127.0.0.1:5001:127.0.0.1:5001 dror@YOUR_LAB_ADDRESS
```

Port 5001 must be free; stop the sample-data preview before starting Compose.
On the future EC2 builder, set `APP_BIND_ADDRESS=0.0.0.0` before `compose up`
only after confirming that its security group restricts access to your IP.

## AWS authentication

Boto3 uses its standard credential chain. Compose forwards
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` from the
current shell, when set. Temporary credentials need all three variables.
An approved instance role is also supported; empty environment values do not
provide credentials. The Terraform builder requires IMDSv2 and permits the
container network hop needed for instance-role credentials.

`iam-read-policy.json` documents the four read actions needed by this app.
It is a policy reference, not an IAM provisioning script. Have the course
administrator approve the identity and permissions. Never put credentials in
source files, Docker build arguments, images, screenshots, or Git history.

Without usable AWS access, `/` returns HTTP 503 with a readable error message.
An empty, successful inventory is shown differently. `/healthz` checks only
the web process and does not prove that AWS access is working.

## Container design

The first Docker stage installs locked Python dependencies. The runtime stage
copies those dependencies and the application, then runs Gunicorn as UID
10001. Compose uses a read-only filesystem, a temporary `/tmp`, and no Linux
capabilities. Logs go to standard output and error. No AWS SDK credentials or
development tests are copied into the image.

## Original bug and correction

The course starter was first committed and built without fixing it. The tag
`stage-3-docker-starter` preserves that checkpoint, including a test that
reproduces its missing-`vpcs` NameError. The fix adds all three missing queries,
restricts AMIs to the current account, handles pagination, and reports AWS
failures without exposing the provider's raw error message.

The current application passes local response-stub tests and container HTTP
checks. Live AWS results and the required EC2 deployment remain unverified.
See [verification](../docs/verification.md).
