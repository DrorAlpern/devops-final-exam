"""Collect machine definitions interactively."""
import logging
from src.machine import Machine
from src.validation import parse_resource, validate_field

logger = logging.getLogger("infra_automation.input")


def _read_field(field, prompt):
    while True:
        raw = input(prompt).strip()
        try:
            if field in ("cpu", "ram"):
                return parse_resource(raw, field)
            value = {"ubuntu": "Ubuntu", "centos": "CentOS"}.get(raw.lower(), raw)
            validate_field(field, value)
            return value
        except ValueError as error:
            logger.warning("Invalid %s: %s", field, error)


def get_user_input():
    machines = []
    names = set()
    while True:
        name = input("\nMachine name (or 'done' to finish): ").strip()
        if name.lower() == "done":
            return machines
        try:
            validate_field("name", name)
            if name.lower() in names:
                raise ValueError("A machine with this name already exists in this run.")
        except ValueError as error:
            logger.warning("Invalid name: %s", error)
            continue
        os_name = _read_field("os", "Simulated OS (Ubuntu/CentOS): ")
        cpu = _read_field("cpu", "CPU cores (e.g. 2 or 2vCPU): ")
        ram = _read_field("ram", "RAM in GB (e.g. 4 or 4GB): ")
        machines.append(Machine(name, os_name, cpu, ram))
        names.add(name.lower())
        print(f"Added {name}.")
