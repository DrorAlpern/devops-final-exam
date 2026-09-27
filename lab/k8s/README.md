# Local Kubernetes files

`kind.sh up` applies the namespace, Moto Deployment/Service, Terraform Job/PVC,
and application Deployment/Service in this folder. The application uses a
published Docker Hub tag. The script creates the Terraform ConfigMap and
supplies dummy Moto credentials to a separate Helm release.

Run `bash lab/kind.sh up` from the repository root. These are local-emulation
resources; no real AWS credentials or EC2 machines are involved.
