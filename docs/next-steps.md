# Remaining work

## Course environment

Confirm the AWS account and access to the required VPC
`vpc-044604d0bfb707142` in `us-east-1`. The brief prohibits creating another
VPC. A personal account cannot be substituted without course guidance.
Obtain the public subnet, allowed source IP, and approved credentials/roles.
Confirm remote Kubernetes access, version, and node architecture too.

## Cloud and CI verification

1. Review Terraform inputs and plan; create the builder only after the account,
   network, and expected cost are agreed. Verify SSH and restricted port 5001.
2. Install Docker and Compose on that builder. Run the published monitor with
   the approved AWS read identity and verify the four inventory sections.
3. Install the course Jenkins environment on the builder. Replace the demo
   password, keep the UI behind SSH, and check the agent's Python/Docker tools.
4. Store a Docker Hub token in Jenkins credential `dockerhub`. Validate the
   Jenkinsfile and run every stage, including a real image push. Keep evidence.
5. Configure and run the Azure equivalent if access is available.
6. Deploy the raw Kubernetes files and verify them in the browser. Then install
   the separate Helm release, test an upgrade and rollback, and test Ingress
   if the course cluster has a suitable controller.

## Completion

Record actual cloud/CI results and screenshots, update each status, and review
for secrets before publishing evidence. Merge the completed `dev` branch into
`main` through a pull request. Final submission waits until the entire rolling
project is complete; no submission has been sent from this repository.
