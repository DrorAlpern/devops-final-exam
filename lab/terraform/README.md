# Terraform against the emulator

The pinned AWS provider sends EC2, ELBv2, STS, and IAM requests to
`http://moto:5000` with dummy credentials. Endpoint values are deliberately
fixed in this local profile. Do not replace them with AWS endpoints.

Both Compose and the kind Job mount this directory at `/config` and supply
a writable `/state` volume for the local backend and provider cache.
The provider lock file is committed. Run this through the parent lab scripts.

The `builder` EC2 and AMI resources are API records. Their IDs and addresses
are not destinations for SSH or real network traffic. The actual workload
runs in Docker or Kubernetes on the Linux host.

Moto includes a fixed image catalog entry used as instance metadata. Terraform
creates a new owned image from the instance record. An explicit network interface
keeps security-group reads stable across repeated plans in Moto. These resources
do not boot an operating system or route real traffic.
