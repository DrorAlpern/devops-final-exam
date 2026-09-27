# Project walkthrough

## What the project does

The program collects machine definitions, validates them, and saves them to a JSON file. It simulates machine creation, then runs a Bash script that installs and configures a real Nginx service on the lab host.

## Execution flow

1. Configure logging to both a file and the terminal.
2. Collect machine details until the user enters `done` at the machine-name prompt.
3. Validate input with `jsonschema`. If a field is invalid, ask for that field again.
4. Create a `Machine` object for each definition. Its `to_dict()` method returns a dictionary that can be saved as JSON.
5. Write the list to a temporary file, then replace the saved configuration after the write completes.
6. Log each simulated machine creation.
7. Run the Bash script through Python's `subprocess` module.
8. Check whether Nginx is installed, deploy the site files, validate the configuration, and confirm that the site responds.

## Key design decisions

- **Virtual environment:** Keeps the project's Python dependencies separate from system packages.
- **Separate modules:** Gives each file a clear responsibility, such as input, validation, logging, or storage.
- **Machine class:** Keeps a machine's details and the operations related to its representation together.
- **Exit codes:** Let a person or an automation tool distinguish success from failure.
- **Repeated runs:** Skip package installation when Nginx is already installed and leave unchanged site files in place.
- **Bash failures:** Python detects a nonzero exit code, logs an error, and exits with a failure status.
- **OS selection:** Ubuntu and CentOS are values in the simulated definitions. The Bash script runs on the lab host.
- **Later stages:** AWS and Terraform are planned for later parts of the course.

## Short demonstration

Connect from PowerShell or Windows Terminal:

```powershell
ssh devops-lab
```

On the Linux host:

```bash
cd ~/infra-automation
source .venv/bin/activate
sudo -v
python infra_simulator.py
```

Enter the following values one line at a time. The CPU value `0` should be rejected; enter `2` when the program asks for CPU again. Type `done` without quotation marks at the next machine-name prompt to finish.

```text
web-01
Ubuntu
0
2
4
done
```

Inspect the saved definition and recent log entries, check the website, and run the automated tests:

```bash
cat configs/instances.json
tail -n 20 logs/provisioning.log
curl -f http://127.0.0.1:8080/
python -m unittest discover -s tests -v
```

Before submitting, review the code and run this demonstration yourself. Be ready to explain the execution flow, the validation error, and the test results.

See the [README](../README.md) for full setup instructions and the [verification record](verification.md) for completed checks.
