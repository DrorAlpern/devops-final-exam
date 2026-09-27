# Project walkthrough

The repository contains the rolling project. Stage 1 is preserved in
`stages/01-infra-automation`; the root application and infrastructure files
cover the later end-to-end work. The separate Docker/Kubernetes assignment
is linked from the root README.

## What runs where

The development machine is an Ubuntu VM on a Proxmox server. Docker runs the
application and its supporting services there. kind runs a real Kubernetes
cluster inside Docker. GitHub stores source code; Docker Hub stores the
application image built and checked by Jenkins.

For the account-free lab, Moto implements the AWS API locally. Terraform
sends requests to that API to create a network and inventory records. The
Flask application uses Boto3 to read the same API and render those records.
The VM, containers, HTTP requests, Jenkins job, and Kubernetes workloads are
real. The EC2 instance, AMI, load balancer, and AWS network inside Moto are
emulated records, not cloud machines.

## Follow the data

1. Run `bash lab/run.sh up` from the repository root.
2. Terraform creates a VPC, two subnets, routing, a security group, and
   instance/image/load-balancer records in Moto.
3. The Flask home page requests EC2 and ELB inventory from Moto.
4. Jinja renders names, states, and resource IDs in the browser.
5. The verification script adds an image, sees it on the page, deletes it,
   and checks that it disappears. This checks the complete request path.

`/healthz` checks that the web process responds. It deliberately does not
prove that inventory is available. The home page returns a useful error
when the inventory API is unavailable instead of showing partial success.

## Why the tools are separate

Terraform describes infrastructure. Docker packages the application.
Jenkins checks source and publishes an image. Kubernetes keeps containers
running and exposes them through a Service. Helm packages Kubernetes
configuration so the same application can be installed, upgraded, and
rolled back with explicit values.

Use [the local instructions](../lab/README.md) for commands and cleanup.
The separate `terraform/` directory preserves the real AWS deployment
option with a configurable account, VPC, and subnet. It has mocked tests;
real AWS deployment has not been performed.
