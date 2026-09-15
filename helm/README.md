# Helm packaging

The application chart is in [flask-aws-monitor](flask-aws-monitor/README.md).
It was initialized with `helm create`, then reduced to the application
Deployment, Service, optional Ingress, shared labels, and installation notes.

Default and customized manifests pass local validation. No Helm release has
been installed into a remote cluster yet.
