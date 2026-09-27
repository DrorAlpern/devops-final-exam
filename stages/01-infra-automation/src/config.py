"""Save definitions without leaving a partial JSON file."""
import json
import os
from pathlib import Path
import tempfile


def save_instances(machines, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=".instances-", suffix=".tmp", delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            json.dump([machine.to_dict() for machine in machines], handle, indent=2)
            handle.write("\n")
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
