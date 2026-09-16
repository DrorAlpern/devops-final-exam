# Local execution evidence

These records summarize observed service runs on the development VM. They
contain no account credentials and make no claim about the AWS builder or
remote course cluster.

- [Jenkins build](jenkins-local.json): source commit, every stage result, and
  the image published by the job. Full logs and scan reports remain in Jenkins.
- [Final Jenkins check](jenkins-local-latest.json): successful rerun after adding
  the local cluster helpers, with its source commit and published digest.
- [Kubernetes exercise](kubernetes-local.json): server version, HTTP checks,
  pod replacement, three-replica upgrade, and one-replica rollback.

The sample-data browser preview is a separate test deployment. The production
application returned a readable 503 when no AWS credentials were supplied.

- [Ingress exercise](ingress-local.json): host routing, expected response content,
  static assets, unknown-host rejection, and browser checks through Traefik.

- [Jenkins after Ingress](jenkins-ingress.json): build #3, including the new
  helper checks, nine deployment resources, and a registry push.

## AWS readiness tests

[Local Jenkins build #4](jenkins-aws-readiness.json) records the 22 Python
tests and ten mocked Terraform plan tests, along with the image publication
and scan results. The live AWS account and network have not been checked.
