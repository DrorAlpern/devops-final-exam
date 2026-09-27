# Execution evidence

[Jenkins build 7](jenkins-review.json) records the successful pipeline from
27 September 2026, including the source commit, image digest, and checks.
The full console and scan reports remain in the local Jenkins build archive.

The local environment uses Moto for AWS APIs; these results do not represent
an EC2 deployment.

[Runtime output](runtime-review.txt) contains excerpts from the Compose and
kind runs, workload status, Helm upgrade/rollback history, and the registry
image digest verified on both application Deployments.

[Browser screenshot](kubernetes-review.png) shows the live application through
the kind Service on 27 September 2026. Moto also supplies a default VPC;
the scripted check counts the VPC created for this lab.
