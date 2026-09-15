# Project walkthrough

## Where the work runs

The Linux development VM is the working environment for editing, tests, and
local Docker containers. GitHub stores the source and its history. Docker Hub
stores built application images. The required AWS `builder` and the remote
Kubernetes cluster are later deployment targets; they do not exist as verified
project environments yet.

## Follow one change through the project

1. **Python and Flask:** `app/app.py` receives a browser request. Boto3 reads
   AWS resources, and the HTML template turns the results into four tables.
2. **Tests:** `tests/test_app.py` supplies known AWS responses through Stubber.
   This checks our query and error-handling logic without needing AWS access.
3. **Docker:** `app/Dockerfile` packages the code, Python, and its dependencies.
   An image is the saved package; a container is a running instance of it.
4. **CI:** `Jenkinsfile` describes checkout, parallel checks, tests, build,
   image scan, and upload. A local Jenkins job has now run all stages
   and published the image; the builder still needs its own Jenkins run.
5. **Kubernetes:** a Deployment keeps the requested number of containers
   running. A Service gives those changing pods a stable access point.
6. **Helm:** the chart generates those Kubernetes files from values, making
   changes such as image version, replica count, and memory limits repeatable.
7. **Terraform:** the Terraform files describe the EC2 builder and its network
   access. Terraform validation checks the configuration; plan and apply
   require the actual course AWS account and existing VPC.

## Three useful distinctions

- A successful local test is evidence about our code, not proof that an AWS
  account grants the required permissions.
- An HTTP 200 from `/healthz` means the web process answers. The inventory
  page must be checked separately because AWS access can fail.
- GitHub contains source files. Docker Hub contains the built image. The
  image tag `b07205ae146d` links the published package to a Git commit.

## What to be ready to explain

The original bug was missing VPC, load-balancer, and AMI queries. The fix
adds those queries, reads every API page, and restricts AMIs to the current
account. Credentials are injected when running the container, not baked
into the image. Security checks initially caught vulnerable OS packages;
changing the base and updating the remaining library cleared the configured
HIGH/CRITICAL scan gate.
