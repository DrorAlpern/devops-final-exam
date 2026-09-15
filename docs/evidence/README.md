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
