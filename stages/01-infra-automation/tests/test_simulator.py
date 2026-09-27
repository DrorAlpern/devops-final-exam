import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from src.machine import Machine
from src.validation import parse_resource, validate_machine

ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def test_valid_machine_and_dictionary(self):
        data = {"name": "web-01", "os": "Ubuntu", "cpu": 2, "ram": 4}
        self.assertEqual(Machine(**data).to_dict(), data)

    def test_invalid_definitions_are_rejected(self):
        valid = {"name": "web-01", "os": "Ubuntu", "cpu": 2, "ram": 4}
        cases = [
            ("name", ""), ("name", "-web"), ("name", "web-"),
            ("name", "../web"), ("name", "web server"), ("name", "a" * 64),
            ("os", "Windows"), ("cpu", 0), ("cpu", -1), ("cpu", True),
            ("cpu", "2"), ("ram", 0), ("ram", 1.5),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    validate_machine({**valid, field: value})

    def test_missing_and_unexpected_fields(self):
        with self.assertRaises(ValueError):
            validate_machine({"name": "web-01"})
        with self.assertRaises(ValueError):
            validate_machine({"name": "web-01", "os": "Ubuntu", "cpu": 2, "ram": 4, "ip": "fake"})

    def test_resource_units(self):
        for raw in ("2", "2vCPU", " 2 VCPU "):
            self.assertEqual(parse_resource(raw, "cpu"), 2)
        for raw in ("4", "4GB", " 4 gb "):
            self.assertEqual(parse_resource(raw, "ram"), 4)
        for raw in ("", "0", "-2", "2.5", "two", "4MB", "2; whoami"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_resource(raw, "cpu")


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.log", "instances.json"),
        )
        self.config = self.root / "configs" / "instances.json"
        self.log = self.root / "logs" / "provisioning.log"

    def run_cli(self, inputs, skip_service=True):
        args = [sys.executable, str(self.root / "infra_simulator.py")]
        if skip_service:
            args.append("--skip-service")
        return subprocess.run(
            args, input=inputs, text=True, capture_output=True,
            cwd=self.temp.name, timeout=20,
        )

    def test_multiple_machines_invalid_input_and_duplicate_name(self):
        result = self.run_cli(
            "web-01\ninvalid-os\nubuntu\n0\n2vCPU\n4GB\nWEB-01\ndb-01\ncentos\n4\n8\ndone\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(self.config.read_text()), [
            {"name": "web-01", "os": "Ubuntu", "cpu": 2, "ram": 4},
            {"name": "db-01", "os": "CentOS", "cpu": 4, "ram": 8},
        ])
        for message in ("Invalid os", "Invalid cpu", "already exists"):
            self.assertIn(message, result.stdout)
        self.assertIn("SIMULATED machine created: web-01", self.log.read_text())
        self.assertIn("Provisioning run finished.", self.log.read_text())

    def test_empty_run_keeps_existing_configuration(self):
        self.config.write_text('[{"existing": true}]\n')
        result = self.run_cli("done\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.config.read_text()), [{"existing": True}])

    def test_unexpected_end_of_input_does_not_save_partial_data(self):
        result = self.run_cli("web-01\nUbuntu\n")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.config.exists())
        self.assertIn("Input ended unexpectedly", self.log.read_text())

    def test_configuration_write_failure_is_reported(self):
        self.config.mkdir()
        result = self.run_cli("web-01\nUbuntu\n2\n4\ndone\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Provisioning failed", self.log.read_text())
        self.assertEqual(list(self.config.parent.glob(".instances-*.tmp")), [])

    def test_service_failure_has_nonzero_exit_and_error_log(self):
        (self.root / "scripts" / "setup_nginx.sh").write_text(
            "#!/usr/bin/env bash\nprintf 'Intentional service failure\\n' >&2\nexit 17\n"
        )
        result = self.run_cli("web-01\nUbuntu\n2\n4\ndone\n", skip_service=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Intentional service failure", result.stdout)
        self.assertIn("exit code 17", self.log.read_text())
        self.assertNotIn("completed successfully", self.log.read_text())

    def test_skip_service_does_not_execute_bash(self):
        (self.root / "scripts" / "setup_nginx.sh").write_text(
            "#!/usr/bin/env bash\nexit 97\n"
        )
        result = self.run_cli("web-01\nUbuntu\n2\n4\ndone\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("service setup was skipped", self.log.read_text())


if __name__ == "__main__":
    unittest.main()
