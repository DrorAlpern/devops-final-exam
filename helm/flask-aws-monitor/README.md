# Flask AWS Monitor chart

Configure the application through `values.yaml` and validate values with
`values.schema.json`. The chart uses an existing AWS credentials Secret;
credential values never belong in Helm values or release history.

| Value | Default | Purpose |
| --- | --- | --- |
| `image.repository` | `droralpern/flask-aws-monitor` | Docker Hub image |
| `image.tag` | `latest` | Release version; prefer a commit tag for reproducibility |
| `image.pullPolicy` | `Always` | Refresh the default latest tag |
| `nodeSelector` | Linux amd64 | Match the published image architecture |
| `replicaCount` | `1` | Number of application pods |
| `aws.region` | `us-east-1` | Region queried by Boto3 |
| `aws.existingSecret` | `aws-credentials` | Secret in the release namespace |
| `extraEnv` | `{}` | Additional non-secret environment values |
| `service.type` | `ClusterIP` | Internal access; LoadBalancer is also supported |
| `service.port` | `5001` | Service port; application container stays on 5001 |
| `resources` | 100m/128Mi requests, 500m/512Mi limits | CPU and memory allocation |
| `ingress.enabled` | `false` | Enable an Ingress when a controller exists |
| `ingress.host` | empty | Required hostname when Ingress is enabled |
| `ingress.className` | empty | Controller class for the actual cluster |
| `ingress.tls` | `[]` | Existing TLS Secret references and hostnames |

The values schema prevents `extraEnv` from overriding the AWS region,
metadata setting, or credential variables. Put credentials only in the referenced Secret.

## Validate without a cluster

From the repository root:

```bash
.venv/bin/python ci/install-tools.py
bash ci/validate-deployment.sh
```

This tests the defaults and a customized release with three replicas,
a different service port, resource limits, LoadBalancer type, and Ingress.
It also checks that zero replicas and enabled Ingress without a host are
rejected. Rendering a LoadBalancer manifest creates no cloud resources.

## Install after cluster access is available

Follow the [Kubernetes prerequisites](../../k8s/README.md) to verify the cluster
and create the existing Secret. The current published image is Linux amd64.
Use a separate release name so this chart does not take ownership of the raw
Kubernetes deployment used for the earlier exercise.

```bash
.tools/bin/helm upgrade --install monitor helm/flask-aws-monitor \
  --namespace devops-monitor --create-namespace \
  --set image.tag=b07205ae146d \
  --set image.pullPolicy=IfNotPresent --wait --timeout 2m
kubectl -n devops-monitor get pods,svc
kubectl -n devops-monitor port-forward service/monitor 5002:5001
```

Open `http://127.0.0.1:5002/` from the machine running port-forward. Check
that the four AWS inventory sections are populated or show genuine empty
results. A healthy pod alone does not verify AWS permissions.

To practice an update, change `replicaCount` with the same upgrade command,
then check the deployment and Helm history. To undo an update, use an existing
revision from the history:

```bash
.tools/bin/helm history monitor -n devops-monitor
.tools/bin/helm rollback monitor REVISION -n devops-monitor --wait
```

Replace `REVISION` with a revision number that actually exists. Remote install,
upgrade, rollback, and Ingress routing still require the remote target. The
[local Ingress exercise](../../ci/local-kubernetes/INGRESS.md) has verified this
chart's routing through Traefik. Enabling a
cloud LoadBalancer may create billable resources; the default is ClusterIP.
