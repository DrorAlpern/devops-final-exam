# Tests and local preview

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/ruff check app tests
.venv/bin/bandit -r app -c pyproject.toml
```

The seven application tests cover the four resource categories, pagination, empty
inventory, missing credentials, denied permissions, partial failures, HTML
escaping, and health checks. Botocore Stubber supplies API responses and
checks request parameters. No real AWS account is contacted.

Fifteen additional tests cover the read-only [AWS preflight](../terraform/PREFLIGHT.md).
They check account and routing decisions, including main-route fallback,
pagination, NAT and blackhole routes, missing credentials, and CLI exit codes.
The repository test command runs all 22 Python tests. The application image
contains only the app, so its container test command selects `test_app.py`.

Ten separate mocked Terraform plan tests run through `bash ci/check-terraform.sh`.
They check the infrastructure rules without creating resources.

Run the same application tests inside the built image:

```bash
sudo docker build -t flask-aws-monitor:dev app
sudo docker run --rm -v "$PWD/tests:/checks:ro" \
  flask-aws-monitor:dev python -m unittest discover -s /checks -p 'test_app.py' -v
```

## Sample-data browser preview

The preview is a test-only WSGI wrapper, separate from the production image.
Every page displays a banner identifying the sample data. It is useful for
checking the layout without AWS access, not for proving a cloud deployment.

```bash
sudo docker run -d --name devops-monitor-preview \
  -p 127.0.0.1:5001:5001 --read-only --tmpfs /tmp:rw,nosuid,noexec,size=64m \
  --cap-drop ALL --security-opt no-new-privileges \
  -v "$PWD/tests:/checks:ro" flask-aws-monitor:dev \
  gunicorn --bind 0.0.0.0:5001 --workers 1 --pythonpath /checks \
  --access-logfile - demo_wsgi:app
```

Stop and remove this preview container before running the real Compose service:

```bash
sudo docker rm -f devops-monitor-preview
```

The tag `stage-3-docker-starter` retains the earlier bug-reproduction test.
That test is deliberately absent from the corrected application branch.
