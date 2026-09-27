# Stage 1 verification

Verified on 15 September 2026, on a fresh Ubuntu Server 24.04 LTS lab VM with Python 3.12.3.

| Requirement | Implementation | Verification |
| --- | --- | --- |
| Repository and virtual environment | Initial setup commit, `.venv`, pinned requirements | Initial commit pushed to GitHub; dependency check passed |
| Dynamic input and library validation | `src/user_input.py`, `src/validation.py`, jsonschema | Invalid OS/CPU, units, duplicate names and multiple-machine CLI tests passed |
| JSON storage | `src/config.py` | Parsed real output; empty-run and write-failure tests passed |
| Machine class and imports | `src/machine.py`, `infra_simulator.py` | Dictionary test and full CLI run passed |
| Bash installation through subprocess | `scripts/setup_nginx.sh`, `run_setup_script()` | First full run installed Nginx; simulated subprocess failure returned a nonzero status |
| Repeatable service configuration | Package check and compare-before-copy | Second full run skipped installation; managed file hashes and modification times were unchanged |
| Logging and errors | Shared `logs/provisioning.log` | Python and Bash start, success, failure and end entries checked |
| Documentation | README, input example, captured output | Setup, execution, expected output and limits documented |

## Executed checks

- 10 automated unittest tests passed.
- Bash syntax check and ShellCheck passed.
- Full run saved two machine definitions as valid JSON.
- Initial run installed Nginx and configured the demo site.
- Second full run completed successfully and skipped package installation.
- `nginx -t` passed.
- Nginx reported both `active` and `enabled`.
- HTTP request to port 8080 succeeded and returned the project page, from both the VM and the Windows workstation.
- Browser checks passed at desktop and mobile widths: no page errors or horizontal overflow; screenshots were visually inspected.
- VM reboot and subsequent SSH, cloud-init and Python environment checks passed before application installation.

## Reproducibility

A fresh clone of implementation commit `2a288f593e56056d17bb6733f8f9fa38d23f76ad` was tested in a temporary directory whose name contains a space. A new virtual environment was created from the pinned requirements. All 10 tests, Bash syntax, ShellCheck and a full CLI run with real service setup passed. The CLI ran with a working directory outside the repository.

## Limits

The automated service-failure test uses a replacement script. The real Bash workflow was exercised on Ubuntu, not on every supported Debian release. Machine definitions are simulated metadata; no real cloud provisioning was tested or claimed.
