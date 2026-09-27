#!/usr/bin/env python3
"""Simulate machine provisioning, then configure Nginx on the local host."""
import argparse
from pathlib import Path
import subprocess
import sys
from src.config import save_instances
from src.logger import setup_logging
from src.user_input import get_user_input

PROJECT_ROOT = Path(__file__).resolve().parent


def run_setup_script():
    script = PROJECT_ROOT / "scripts" / "setup_nginx.sh"
    # Bash writes its own entries to the same provisioning log.
    result = subprocess.run(
        ["bash", str(script)], cwd=PROJECT_ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if result.stdout:
        print(result.stdout, end="", flush=True)
    result.check_returncode()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-service", action="store_true",
        help="Run the simulation without installing or configuring Nginx.",
    )
    args = parser.parse_args(argv)
    try:
        logger = setup_logging(PROJECT_ROOT / "logs" / "provisioning.log")
    except OSError as error:
        print(f"Cannot initialize logging: {error}", file=sys.stderr)
        return 1

    logger.info("Provisioning run started.")
    print("Machine creation is simulated.")
    if not args.skip_service:
        print("After the simulation, Nginx will be configured on this Linux host.")
    try:
        machines = get_user_input()
        if not machines:
            logger.info("No machines entered; existing configuration was kept.")
            return 0
        config_file = PROJECT_ROOT / "configs" / "instances.json"
        save_instances(machines, config_file)
        logger.info("Saved %d machine definition(s) to %s.", len(machines), config_file)
        for machine in machines:
            machine.log_creation()
        if args.skip_service:
            logger.info("Simulation completed; service setup was skipped.")
        else:
            logger.info("Starting Bash service setup.")
            run_setup_script()
            logger.info("Provisioning simulation and service setup completed successfully.")
        return 0
    except KeyboardInterrupt:
        logger.warning("Run interrupted by the user.")
        return 130
    except EOFError:
        logger.error("Input ended unexpectedly. Finish machine entry with 'done'.")
        return 1
    except subprocess.CalledProcessError as error:
        logger.error("Service setup failed with exit code %s. See provisioning.log.", error.returncode)
        return 1
    except (OSError, ValueError) as error:
        logger.error("Provisioning failed: %s", error)
        return 1
    finally:
        logger.info("Provisioning run finished.")


if __name__ == "__main__":
    sys.exit(main())
