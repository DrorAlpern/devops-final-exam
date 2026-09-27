# Chart templates

These templates generate the Deployment and Service. The Ingress template is
optional, as specified in the brief. `_helpers.tpl` keeps resource names and
labels consistent; `NOTES.txt` prints connection instructions.

Run `bash ci/validate-deployment.sh` from the repository root to render and
validate the chart. This README is excluded from the chart by `.helmignore`.
