# Local Kubernetes lab

This single-node kind cluster runs Kubernetes 1.35.8 inside Docker on the
Linux development VM. It is a real local cluster, separate from the remote
course environment. No AWS account or cloud resource is used.

## Start and verify

Stop Jenkins first on the 4 GiB VM to keep room for the exercise:

```bash
sudo docker stop devops-jenkins-agent-1 devops-jenkins-controller-1
bash ci/local-kubernetes/start.sh
bash ci/local-kubernetes/verify.sh
```

The installer verifies the kind and kubectl release checksums. The cluster
API binds only to `127.0.0.1:16443`. Its access file is stored outside Git at
`~/.config/devops-kubernetes/kubeconfig` with mode 0600. No host Docker group
membership changes are needed.

The verification script refuses a different context or API address. It:

1. Applies the production Deployment and Service in `devops-monitor`.
2. Uses empty local credentials and checks health 200 plus inventory 503.
3. Deletes one test pod and checks that the Deployment replaces it.
4. Installs the Helm chart in `devops-helm-local` with one replica.
5. Upgrades to the CI-published image tag and three ready replicas.
6. Rolls back and checks the previous tag and one ready replica.

Temporary HTTP port forwards are closed after verification. Results go to
`reports/`; reviewed summaries are kept in [the evidence folder](../../docs/evidence/README.md).
The two image tags exercise version selection; the application source itself
has not changed between these builds.

## View the sample-data deployment

```bash
bash ci/local-kubernetes/preview.sh
```

Keep it running. From the workstation, open an SSH tunnel:

```bash
ssh -N -L 15003:127.0.0.1:15003 devops-lab
```

Visit `http://127.0.0.1:15003`. The page explicitly states that its resources
are samples. The preview uses a separate namespace and mounts only the test
wrapper from `tests/demo_wsgi.py`; the production image and Helm chart do not
enable sample data.

## Inspect or pause the lab

```bash
export KUBECONFIG="$HOME/.config/devops-kubernetes/kubeconfig"
.tools/bin/kubectl get pods -A
.tools/bin/helm history monitor -n devops-helm-local
```

After stopping active port forwards, pause the local node when switching
back to a Jenkins build:

```bash
sudo docker stop devops-local-control-plane
```

Resume it with `sudo docker start devops-local-control-plane`, then run
`bash ci/local-kubernetes/start.sh` to wait for readiness. Its Docker network
and stored node state are retained. If the lab is no longer needed, kind's
`delete cluster --name devops-local` command removes only this named lab;
that discards the local workloads and Helm history.

The optional [Ingress exercise](INGRESS.md) adds hostname-based access and
checks both application routes through a real local controller.

The remote course cluster and AWS-backed inventory still need their target
environments. A local browser result does not verify those environments.
