# Practice session

Use [the local lab](../lab/README.md) to start the system. Explain each step
in your own words before moving to the next one.

1. Open the inventory page. Identify the running instance, VPC, image, and
   load balancer. Explain why the local-emulation notice is visible.
2. Open `lab/terraform/main.tf`. Find the VPC and two subnets. Explain how
   a Terraform reference connects a subnet to its VPC.
3. Run `bash lab/run.sh plan`. A second plan should report no changes.
4. Run `bash lab/run.sh verify`. Explain how the temporary-image check proves
   that the application reads changing API data rather than fixed HTML.
5. Open `app/app.py`. Follow the request from the Flask route through Boto3
   to the template. Compare the home page with `/healthz`.
6. Start the kind profile and run `bash lab/kind.sh verify`. Observe pod
   replacement, Helm scaling, and rollback. These affect real containers.
7. Open `Jenkinsfile`. Follow checkout, checks, tests, image build, security
   scan, smoke test, and registry publication. Explain why a failed check
   must stop publication.
8. Find the first-stage Python/Bash project in `stages/01-infra-automation`.
   Explain what it simulates and what it configures on the Linux host.

A useful explanation of the lab boundary: "My application and automation
run locally. Terraform provisions AWS-style records in Moto, and Boto3
reads them. I tested Kubernetes with kind. I have not deployed EC2 in AWS."

Stop only the dedicated lab resources with the cleanup commands in the
local guide. Do not delete the shared kind cluster to stop one assignment.
