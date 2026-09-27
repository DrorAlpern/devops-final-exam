# Local Kubernetes files

These are the actual manifests applied by `bash lab/kind.sh up`:

- `namespace.yaml`: isolated `devops-submission` namespace.
- `moto.yaml`: single emulator Deployment and internal Service.
- `terraform.yaml`: Terraform Job and persistent state volume.
- `monitor.yaml`: application Deployment.
- `service.yaml`: application's ClusterIP Service.

The script generates a ConfigMap from `lab/terraform` and supplies the image
it built and loaded into kind. The `local-lab` tag in the raw file is a
placeholder for that local build, not a Docker Hub release. All credentials
shown here are intentionally non-secret dummy values for Moto.

Only the application process runs with the requested replicas. The emulator
runs one instance with Recreate strategy because its inventory is in memory.
Rerun the up command after an emulator restart to reconcile Terraform state.

No public load balancer, AWS account, or real Kubernetes credential is included
in these files. See the parent [run instructions](../README.md).
