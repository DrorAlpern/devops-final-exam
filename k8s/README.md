# Kubernetes deployment

These manifests run the published `a56aa0c325f4` image in the
`devops-monitor` namespace. The image is built for Linux amd64. Confirm that
the remote cluster has compatible nodes before deployment.

## Prerequisites

Use the approved course cluster and verify its context before making changes:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl apply -f k8s/namespace.yaml
```

Create an `aws-credentials` Secret in this namespace from a private environment
file outside the repository. The file must contain `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY`; add `AWS_SESSION_TOKEN` for temporary credentials.
Use the course-approved read-only identity. Do not print or commit the file.

```bash
chmod 600 "$HOME/.config/devops-monitor/aws.env"
kubectl -n devops-monitor create secret generic aws-credentials \
  --from-env-file="$HOME/.config/devops-monitor/aws.env"
```

This expects an existing private file. It does not create credentials.
The Secret is required: a missing Secret prevents the pod from starting.
Instance-metadata credential discovery is disabled in Kubernetes, so the app
does not accidentally use the worker node's identity.

## Deploy and check

```bash
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl -n devops-monitor rollout status deployment/flask-aws-monitor --timeout=120s
kubectl -n devops-monitor get pods,svc
kubectl -n devops-monitor port-forward --address 127.0.0.1 \
  service/flask-aws-monitor 5002:5001
```

Open `http://127.0.0.1:5002/` on the computer running port-forward. If that is
the development VM, forward its port 5002 to your computer through SSH too.
The default ClusterIP Service does not create a paid public load balancer.

The web process runs as UID 10001 with a read-only filesystem and temporary
memory-backed storage. Startup, readiness, and liveness probes use `/healthz`.
A Ready pod proves process health, not AWS access: check the actual inventory
page and its four resource categories separately. Renew expired credentials
and restart the deployment so it reads the updated Secret.

## Validation status

The files pass strict kubeconform validation against Kubernetes 1.35.0.
That schema version is a local check target, not a claim about the course
cluster. Cluster access, server-side validation, rollout, and browser
verification with AWS data remain pending. See [verification](../docs/verification.md).
