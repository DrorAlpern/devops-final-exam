"""A machine definition used by the provisioning simulation."""
import logging
from src.validation import validate_machine

logger = logging.getLogger("infra_automation.machine")


class Machine:
    def __init__(self, name, os, cpu, ram):
        validate_machine({"name": name, "os": os, "cpu": cpu, "ram": ram})
        self.name = name
        self.os = os
        self.cpu = cpu
        self.ram = ram

    def to_dict(self):
        return {"name": self.name, "os": self.os, "cpu": self.cpu, "ram": self.ram}

    def log_creation(self):
        logger.info(
            "SIMULATED machine created: %s | %s | %s vCPU | %s GB RAM",
            self.name, self.os, self.cpu, self.ram,
        )
