# Flask AWS monitor: starter checkpoint

This checkpoint packages the application supplied in the course brief. Its
missing VPC query is deliberately preserved for the required debugging stage.
The load-balancer and AMI queries are also missing. This is not a completed
application and it must not be deployed as a working release.

## Build and run

```bash
sudo docker build -t flask-aws-monitor:starter app
sudo docker run --rm -p 127.0.0.1:5001:5001 \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
  flask-aws-monitor:starter
```

Provide credentials through the standard environment variables. Do not add
them to the Dockerfile, build arguments, source, or Git history. Use port
`5001:5001` on the EC2 builder only after its restricted security group has
been verified. The local example binds only to the loopback interface.

The image uses two stages: the first installs the locked dependencies, and
the second copies them into the runtime image. It runs Gunicorn as a non-root
user. Gunicorn imports the module without invoking the starter code's
`app.run(debug=True)` development entry point.

## Reproduce the expected bug locally

```bash
.venv/bin/python tests/check_starter_bug.py
```

This uses a Botocore response stub for EC2, then confirms that the original
route raises `NameError` for `vpcs`. It makes no AWS calls. A successful test
means the starter defect was reproduced; it does not mean the application is
working. The next feature branch fixes it.

No build or run on a real EC2 builder has been completed yet.
