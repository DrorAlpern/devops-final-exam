# Infrastructure Automation

A rolling DevOps course project. Stage 1 collects and validates machine definitions, simulates provisioning, and uses Bash to install and configure Nginx.

**Machine provisioning is simulated. Nginx setup is real and runs on the Linux host once per non-empty run, unless you use `--skip-service`.** No VM, cloud resource, or network connection is created for a machine definition.

## Requirements

- Full workflow tested on Ubuntu Server 24.04 LTS with Python 3.12 and systemd.
- Git, Python with `venv`, Bash, and curl.
- Internet access for Python dependencies and initial Nginx installation.
- A user with sudo access. Run Python as your normal user.

The Bash installer accepts Ubuntu and Debian; the live checks for this submission were performed on Ubuntu. The OS value in a machine definition is simulation metadata, so selecting CentOS does not install CentOS or run commands on a CentOS server.

## Setup

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv git curl
git clone https://github.com/DrorAlpern/devops-final-exam.git
cd devops-final-exam/stages/01-infra-automation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

This stage is included in the public rolling-project repository. Its original source checkpoint is `9bc1f928dbb63ca2f5d55fea733acb921088c530`; the setup path above was updated for this combined layout.

## Run

```bash
sudo -v
python infra_simulator.py
```

Enter each machine's details. Type `done` at the machine-name prompt to finish. Invalid fields are requested again.

| Field | Accepted values | Stored value |
| --- | --- | --- |
| Name | 1–63 letters, digits or hyphens; first and last character must be alphanumeric | String |
| OS | Ubuntu or CentOS, case-insensitive | `Ubuntu` or `CentOS` |
| CPU | Positive whole number, such as `2` or `2vCPU` | Integer vCPU count |
| RAM | Positive whole number, such as `4` or `4GB` | Integer GB count |

Names must be unique within a run, ignoring letter case. `done` is reserved for ending input.

Example input, one line at a time:

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

The run writes `configs/instances.json`, logs each simulated machine creation, and calls `scripts/setup_nginx.sh`. Representative output:

```text
INFO: SIMULATED machine created: web-01 | Ubuntu | 2 vCPU | 4 GB RAM
INFO: SIMULATED machine created: db-01 | CentOS | 4 vCPU | 8 GB RAM
INFO: Starting Bash service setup.
... Nginx setup completed. Demo site: http://127.0.0.1:8080
INFO: Provisioning simulation and service setup completed successfully.
INFO: Provisioning run finished.
```

A complete captured run is in [docs/example-output.txt](docs/example-output.txt). That capture uses piped input, so prompts appear on the same lines. [configs/instances.example.json](configs/instances.example.json) shows the JSON format.

Each non-empty run replaces the saved machine list. An empty run preserves it and skips service setup. A failed write does not leave a partially written JSON file. Runtime JSON and logs are excluded from Git.

To run only the simulation:

```bash
python infra_simulator.py --skip-service
```

## Nginx setup

The Bash script checks whether the package is installed, installs it if necessary, and deploys:

- `configs/nginx.conf` to `/etc/nginx/sites-available/infra-automation`, enabled by a symlink in `sites-enabled`.
- `configs/index.html` to `/var/www/infra-automation/index.html`.

The demo listens on port **8080**. The script checks Nginx configuration, enables and starts the service, reloads it, and checks its HTTP response. Repeated runs skip package installation and keep unchanged configuration files.

```bash
curl -f http://127.0.0.1:8080/
systemctl status nginx
```

From another computer, use `http://<lab-ip>:8080/`. Network access to the lab must already be available; this project does not change firewall rules.

## Logs and failures

Python uses the standard `logging` module. Bash adds timestamped entries to the same file:

```bash
tail -n 50 logs/provisioning.log
```

The log includes run start/end, validation warnings, machine creation, service actions and errors. Detailed package-manager output goes to the log.

- Exit `0`: successful run, including a deliberately empty run.
- Exit `1`: file, service, or unexpected end-of-input failure.
- Exit `130`: interrupted by the user.

A service failure keeps the validated JSON for inspection. The program reports the failure instead of reporting service success.

## Tests

```bash
python -m unittest discover -s tests -v
bash -n scripts/setup_nginx.sh
```

The automated tests run the CLI in temporary project copies. Service-error tests use a replacement Bash script, so the test suite does not install Nginx. It covers invalid definitions and units, duplicate names, multiple machines, empty input, incomplete input, JSON write failures, skipped setup and subprocess failures.

Live checks are recorded in [docs/verification.md](docs/verification.md). For an explanation of the execution flow and a short demonstration, see the [project walkthrough](docs/walkthrough.md).

## Code layout

```text
infra-automation/
|-- infra_simulator.py
|-- src/
|   |-- machine.py
|   |-- user_input.py
|   |-- validation.py
|   |-- config.py
|   `-- logger.py
|-- scripts/setup_nginx.sh
|-- configs/
|-- logs/
|-- tests/test_simulator.py
|-- docs/
|-- requirements.txt
`-- README.md
```

The entry point connects input, JSON storage, simulated provisioning and Bash execution. `Machine` holds one validated definition, returns its dictionary form and logs its simulated creation.

The later Terraform, Docker, Jenkins, and Kubernetes work is in the repository root. No AWS credentials or Terraform setup are needed for Stage 1.

## Documentation

All project documentation is maintained in English, including the local copies, files on the lab host, and files on GitHub.
