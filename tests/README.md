# Tests

`check_starter_bug.py` reproduces the course starter application's missing
VPC query using a Botocore EC2 stub. Run it with:

```bash
.venv/bin/python tests/check_starter_bug.py
```

The test passed on the host, and the same defect was verified inside the
Docker image while running as UID 10001. These checks make no AWS API calls.
The application is intentionally incomplete at this Git checkpoint.
