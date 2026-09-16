# A short practice session

The commands below run on `devops-lab` from `~/devops-final-exam`.
They inspect the current lab; the full exercise scripts also make controlled
changes inside the dedicated local environment.

## 1. Identify the three places

GitHub stores source code and commit history. Docker Hub stores the image
built from that code. The Linux VM runs Jenkins, Docker, and the local kind
cluster. AWS will later provide the course builder and real inventory data.

Open `Jenkinsfile` and find the parallel Linting and Security Scan stages.
A failed required check stops publication. In Jenkins build #5, follow one
commit from checkout to its matching Docker Hub tag `47b6bf08a303`.

## 2. See what Kubernetes keeps running

```bash
export KUBECONFIG="$HOME/.config/devops-kubernetes/kubeconfig"
.tools/bin/kubectl -n devops-monitor get deployment,pods,service
```

The Deployment defines the desired number of copies. Pods run those copies.
The Service routes requests to ready pods, even when a pod is replaced.
The local verification exercise deleted a pod and observed a new ready one.

## 3. Read the Helm history

```bash
.tools/bin/helm history monitor -n devops-helm-local
.tools/bin/helm get values monitor -n devops-helm-local
```

The first exercise installed one replica, upgraded to three replicas and a
new image tag, then rolled back. A rollback creates another revision that
restores earlier settings; it does not erase the deployment history.

## 4. Explain the two HTTP results

`/healthz` returns 200 when the web process answers. The inventory page returns
503 when the required AWS access is unavailable. A green Kubernetes readiness
check therefore does not prove that the AWS account or IAM policy works.

The separate sample preview shows the intended tables and carries a visible
sample-data notice. It helps review the layout without pretending to have a
working cloud connection.

## 5. Follow a request through Ingress

Open `http://preview.localhost:15004` while the local tunnel is running.
The hostname selects an Ingress rule. Traefik sends the request to the preview
Service, which selects the ready pod. The same controller routes
`monitor.localhost` to the separate Helm application Service.

The [Ingress exercise](../ci/local-kubernetes/INGRESS.md) shows the commands
and expected responses. Explain why an unknown hostname returns 404, while
the application's missing-AWS-access page returns 503.

## 6. Explain what remains

The required VPC belongs to a particular AWS account. Copying its ID into
another account does not create access to that network. Once course access
is confirmed, review a Terraform plan, create the builder, run the same
application and CI workflow there, and verify the remote Kubernetes target.

Be ready to explain the original missing resource queries, pagination,
account-owned AMIs, credentials at runtime, and why security checks can block
a build. Each of those decisions is visible in the source and test history.
