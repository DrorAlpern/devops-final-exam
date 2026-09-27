# Terraform tests

`builder.tftest.hcl` uses a mocked AWS provider and plan-only runs. It checks
the builder's ports, key reference, network inputs, encryption, and instance
metadata settings. From the repository root, run `bash ci/check-terraform.sh`.
No resources are created by these tests.
