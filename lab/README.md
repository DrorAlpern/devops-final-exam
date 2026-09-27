# Local lab

This setup runs the Flask application against Moto, a local AWS API emulator.
Terraform creates network, instance, image, and load-balancer records there.
The records are simulated; the application containers run on the Linux host.

## Requirements

- Linux amd64, Git, Docker Engine, and Docker Compose.
- For Kubernetes: Python 3. The setup script installs pinned kind, kubectl,
  and Helm binaries under `.tools/bin`.
- Internet access for images, packages, and providers.
- About 4 GiB RAM for this lab alone. Run Jenkins separately on a small host.

Scripts use Docker directly when permitted, otherwise passwordless sudo.

## Docker Compose

From the repository root:

```bash
bash lab/run.sh up
bash lab/run.sh verify
bash lab/run.sh plan
```

Open **http://127.0.0.1:15005**. The verification checks the four resource
categories and HTTP responses. The second Terraform plan should have no changes.
For a remote host, keep this workstation tunnel open:

```bash
ssh -N -L 15005:127.0.0.1:15005 user@linux-host
```

Then open the same address on the workstation. The local profile uses dummy
keys and fixed Moto endpoints. Terraform state stays in a Docker volume.

## Kubernetes and Helm

```bash
bash lab/run.sh down
bash lab/kind.sh up
bash lab/kind.sh verify
```

The script creates a separate `devops-submission` kind cluster. It runs Moto
and a Terraform Job, then deploys the published Docker Hub image through the
raw [Kubernetes files](k8s/README.md) and a separate Helm release. Verification
checks inventory, increases Helm replicas to two, and rolls back to one.

To view the raw Deployment:

```bash
export KUBECONFIG="$HOME/.config/devops-submission/kubeconfig"
.tools/bin/kubectl --context kind-devops-submission -n devops-submission \
  port-forward --address 127.0.0.1 service/monitor 15006:5001
```

Open `http://127.0.0.1:15006`. For a remote host, use an SSH tunnel on port
15006. Use `service/monitor-helm` to view the Helm release instead.

## Cleanup and restarts

```bash
bash lab/run.sh down
bash lab/kind.sh down
```

Compose removes this lab's containers and state volume. Kubernetes removes
only the `devops-submission` namespace. To remove its dedicated cluster too,
run `.tools/bin/kind delete cluster --name devops-submission` with Docker access.
Moto keeps records in memory; after it restarts, rerun the relevant up command.

If another kind cluster is already running and kube-proxy reports `too many
open files`, check the host's inotify limits. See the official
[kind troubleshooting guide](https://kind.sigs.k8s.io/docs/user/known-issues/#pod-errors-due-to-too-many-open-files).
The project scripts do not change host kernel settings.
