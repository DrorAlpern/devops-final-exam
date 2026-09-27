# Application tests

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
bash ci/check.sh test
```

Nine application tests cover the four resource lists, pagination, empty results,
API failures, HTML escaping, health, and the local-emulation notice. Botocore
Stubber supplies responses without contacting AWS. The same command runs the
ten Stage 1 tests. Terraform's ten mocked plan tests run separately with
`bash ci/check-terraform.sh`.
