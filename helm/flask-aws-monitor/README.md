# Flask AWS Monitor chart

The chart deploys the application with a Deployment and Service. It accepts an
existing credentials Secret. The Ingress template is the brief's optional bonus
and is disabled by default.

| Value | Default | Use |
| --- | --- | --- |
| `image.repository` | `droralpern/flask-aws-monitor` | Published image |
| `image.tag` | `latest` | Image version |
| `image.pullPolicy` | `Always` | Pull behavior |
| `replicaCount` | `1` | Application replicas |
| `aws.region` | `us-east-1` | API region |
| `aws.existingSecret` | `aws-credentials` | Credentials Secret in the release namespace |
| `extraEnv` | `{}` | Additional environment settings, such as the Moto endpoint |
| `service.type` | `ClusterIP` | Service type |
| `service.port` | `5001` | Service port |
| `resources` | See values.yaml | CPU and memory requests/limits |
| `ingress.enabled` | `false` | Optional Ingress |

The image targets Linux amd64. `values.schema.json` rejects invalid values and
keeps credential variables in the Secret instead of `extraEnv`.

## Run and test

The complete local installation is `bash lab/kind.sh up` from the repository
root. It creates the dummy Moto Secret and sets the endpoint for this chart.
`bash lab/kind.sh verify` tests scaling and rollback.

To install against a separately configured AWS identity:

```bash
helm upgrade --install monitor helm/flask-aws-monitor   --namespace devops-monitor --create-namespace --wait
kubectl -n devops-monitor get pods,svc
kubectl -n devops-monitor port-forward service/monitor 5001:5001
```

Create the `aws-credentials` Secret first as described in [k8s](../../k8s/README.md).
Then open `http://127.0.0.1:5001`. That real-AWS path has not been executed.

Change values with `helm upgrade`, inspect revisions with `helm history`, and
use `helm rollback` with an existing revision to undo a change.
`bash ci/validate-deployment.sh` renders and validates the chart without a cluster.
