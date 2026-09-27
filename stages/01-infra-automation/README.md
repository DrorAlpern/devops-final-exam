# Infrastructure Automation - Stage 1

A Python CLI collects machine definitions, validates them with jsonschema,
saves JSON, and logs simulated provisioning. It then calls a Bash script to
install and configure Nginx on the Linux host.

**Machine creation is simulated. Nginx installation is real.** The full workflow
was tested on Ubuntu Server 24.04 with Python 3.12 and systemd.

## Setup

Requirements: Git, Python with venv, Bash, curl, internet access, and a user
with sudo access. From the repository root:

```bash
cd stages/01-infra-automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
sudo -v
python infra_simulator.py
```

Enter each machine's name, operating system, CPU, and RAM. Type `done` at the
name prompt to finish. Example input:

```text
web-01
Ubuntu
2vCPU
4GB
db-01
CentOS
4
8
done
```

Names must contain 1-63 letters, digits, or hyphens, start and end with a letter
or digit, and be unique within the run. OS accepts Ubuntu or CentOS. CPU and
RAM accept positive whole numbers, optionally followed by `vCPU` or `GB`.
Invalid fields are requested again. The OS is only simulation metadata.

The CLI writes `configs/instances.json` and `logs/provisioning.log`. Each
non-empty run replaces the saved machine list; an empty run preserves it.
Use `python infra_simulator.py --skip-service` to avoid changing Nginx.

Expected output includes:

```text
INFO: SIMULATED machine created: web-01 | Ubuntu | 2 vCPU | 4 GB RAM
INFO: Starting Bash service setup.
... Nginx setup completed. Demo site: http://127.0.0.1:8080
INFO: Provisioning simulation and service setup completed successfully.
```

A captured run is in [docs/example-output.txt](docs/example-output.txt).

## Nginx and errors

The Bash script installs Nginx if absent, copies the supplied site configuration
and HTML, checks the Nginx configuration, reloads the service, and tests port 8080.
Repeated runs skip installation and keep unchanged files.

```bash
curl -f http://127.0.0.1:8080/
tail -n 50 logs/provisioning.log
```

Exit codes are 0 for success, 1 for a file/service/input failure, and 130 for
interruption. A service failure keeps the validated JSON and reports the error.
Logs contain validation warnings, simulated creation, service actions, and errors.

## Code and tests

`src/machine.py` contains the Machine class. Other modules handle input,
validation, JSON storage, and logging. `infra_simulator.py` connects those
steps and calls `scripts/setup_nginx.sh` through subprocess.

```bash
python -m unittest discover -s tests -v
bash -n scripts/setup_nginx.sh
```

Tests use temporary files and a replacement service script; they do not install
Nginx. [Verification](docs/verification.md) records the original live checks.
The preserved source checkpoint is `9bc1f928dbb63ca2f5d55fea733acb921088c530`.
