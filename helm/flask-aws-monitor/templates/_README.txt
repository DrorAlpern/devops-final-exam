# Chart templates

Deployment, Service, and optional Ingress templates share the labels in
`_helpers.tpl`. Values are defined in the parent chart directory. The leading
underscore keeps this documentation out of the rendered Kubernetes manifests.
`NOTES.txt` prints the post-install checks.
