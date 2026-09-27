# Local AWS API lab

This is the default demonstration environment for the rolling project. It
runs the actual Flask application against Moto 5.2.3, a local AWS API emulator.
There is no AWS login, paid lab account, or cloud resource in this workflow.

Terraform creates a VPC, two subnets, a gateway, routing, a restricted security
group, an EC2 record named `builder`, an AMI, and a load-balancer record.
Boto3 queries those API resources on each browser request. A lifecycle check
creates an additional AMI record, confirms it appears, deletes it, and confirms
it disappears. The application uses its normal query code, not a fixed HTML
preview or mocked Python function.

## Requirements

- Linux amd64; Docker Engine with Compose; Git.
- For kind: Python 3, curl, and access to Docker. The supplied installer
  downloads checksum-verified kind, kubectl, and Helm into `.tools/bin`.
- 4 GiB RAM is sufficient for this lab alone; run Jenkins separately. Stop other optional labs if the host is short of resources.
  6 GiB or more gives additional headroom. Allow space for container images.
- Internet access for initial image, Python package, and provider downloads.

The scripts use Docker directly when permitted, otherwise passwordless sudo
on the dedicated lab host. No Docker group membership is changed.

## Compose demonstration

From the repository root:

```bash
bash lab/run.sh up
bash lab/run.sh verify
bash lab/run.sh plan
```

Open **http://127.0.0.1:15005**. A notice identifies the inventory as local
emulation. The second command verifies HTTP and resource lifecycle behavior.
The plan command should report no changes after a successful run.

When Docker runs on another Linux machine, keep this workstation tunnel open,
replacing the SSH destination with your host:

```bash
ssh -N -L 15005:127.0.0.1:15005 user@linux-host
```

Then open the same browser address on the workstation.

The application and Moto share an internal Docker network. The monitor has a separate web network for its localhost port. The Terraform
tools container has a second network for provider downloads. No real AWS
credentials are mounted or passed; the provider endpoints and dummy keys are
explicitly local. Terraform state lives in a named Docker volume.

## Kubernetes and Helm demonstration

Stop Compose first if memory is limited:

```bash
bash lab/run.sh down
bash lab/kind.sh up
bash lab/kind.sh verify
```

The up script creates or reuses the dedicated `kind-devops-submission` context,
builds and loads an image tagged from its source contents, and applies the
files in [k8s](k8s/README.md). A ConfigMap supplies the same Terraform code and
lock file used by Compose; a Job applies it against the Moto Service.
A PVC preserves Terraform state across Job reruns. The Helm application uses
the same emulator and image.

The verify script checks live inventory, replaces an application pod, upgrades
the Helm release to two replicas, and rolls it back to one. It does not
change the separate Docker/Kubernetes module assignment.

To view the raw Deployment:

```bash
export KUBECONFIG="$HOME/.config/devops-submission/kubeconfig"
.tools/bin/kubectl --context kind-devops-submission -n devops-submission \
  port-forward --address 127.0.0.1 service/monitor 15006:5001
```

For a remote Linux host, add a workstation SSH tunnel on port 15006.
Use `service/monitor-helm` instead to view the Helm release.

## Restart and cleanup

Moto's API records are held in memory. After the emulator restarts, rerun the
appropriate up command. Terraform refreshes its state and recreates missing
resources. Both up commands are repeatable.

```bash
bash lab/run.sh down
bash lab/kind.sh down
```

Compose cleanup removes only this lab's containers and state volume.
Kubernetes cleanup removes only the `devops-submission` namespace, including
its disposable state PVC. The dedicated kind cluster remains available for another run. Remove only this cluster with `kind delete cluster --name devops-submission` when finished; other clusters are untouched.

## What this proves

The exercise proves Terraform/provider/API integration, real container
execution, Boto3 inventory reads, Kubernetes rollout/recovery, and Helm
release management. Moto does not boot an EC2 machine, route real VPC traffic,
or reproduce all IAM behavior. Jenkins runs on the Linux development host.
The cloud deployment configuration is available under [terraform](../terraform/README.md)
but is a separate, unexecuted target.

References: [Moto server mode](https://docs.getmoto.org/en/latest/docs/server_mode.html)
and [EC2 API coverage](https://docs.getmoto.org/en/latest/docs/services/ec2.html).

## Host troubleshooting

If a second kind cluster reports `too many open files` in kube-proxy logs,
check the host's inotify limits. These limits are shared by all containers.
The scripts do not alter host kernel settings. See the official
[kind known issues](https://kind.sigs.k8s.io/docs/user/known-issues/#pod-errors-due-to-too-many-open-files)
for the diagnosis and host-specific remedy. Startup checks wait for Service
routing, DNS, and storage as well as node readiness.
