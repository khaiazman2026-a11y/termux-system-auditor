"""Tests for report generation and export."""

import json
import tempfile
import unittest
from datetime import datetime as DateTime
from pathlib import Path
from unittest.mock import patch

from reports.generator import export_reports, generate_terminal_report


class FixedDateTime:
    @classmethod
    def now(cls, tz=None):
        return DateTime(2026, 1, 1, 12, 0, 0, tzinfo=tz)


class TestReportGeneration(unittest.TestCase):
    def setUp(self):
        self.data = {
            "audit_time": "2026-01-01T12:00:00+00:00",
            "hardware": {
                "architecture": "aarch64",
                "cpu_threads": 8,
                "ram": {
                    "total_bytes": 8192,
                    "available_bytes": 4096,
                },
                "storage": {
                    "available_bytes": 16384,
                },
            },
            "software": {
                "operating_system": "Android",
                "python_version": "3.14.10",
                "is_termux": True,
                "commands": {
                    "git": {"installed": True},
                },
            },
            "dependencies": {
                "numpy": {
                    "installed": True,
                    "version": "2.5.4",
                },
            },
            "ai_readiness": {
                "llm": {
                    "engines": {
                        "llama-server": {"installed": True},
                    },
                    "models": [
                        {
                            "name": "model.gguf",
                            "size_bytes": 1024,
                        },
                    ],
                    "model_count": 1,
                    "readiness": {
                        "status": "LIMITED",
                        "reason": "Runtime not tested.",
                    },
                },
                "tts": {
                    "engines": {
                        "Piper": {"installed": False},
                    },
                    "readiness": {
                        "status": "NOT READY",
                        "reason": "No engine detected.",
                    },
                },
                "image_generation": {
                    "engines": {
                        "sd-cli": {"installed": True},
                    },
                    "models": [],
                    "model_count": 0,
                    "readiness": {
                        "status": "UNKNOWN",
                        "reason": "No model detected.",
                    },
                },
            },
        }

    def test_terminal_report_contains_sections(self):
        report = generate_terminal_report(self.data)

        self.assertIn("TERMUX SYSTEM AUDITOR", report)
        self.assertIn("HARDWARE", report)
        self.assertIn("SOFTWARE", report)
        self.assertIn("PYTHON DEPENDENCIES", report)
        self.assertIn("LOCAL LLM", report)
        self.assertIn("LOCAL TEXT-TO-SPEECH", report)
        self.assertIn("IMAGE GENERATION", report)

    def test_terminal_report_shows_dependency_inspection_error(self):
        self.data["dependencies"]["numpy"] = {
            "installed": None,
            "version": None,
            "inspection_status": "ERROR",
        }

        report = generate_terminal_report(self.data)

        self.assertIn("INSPECTION ERROR", report)

    def test_terminal_report_shows_ai_engine_inspection_error(self):
        self.data["ai_readiness"]["tts"]["engines"]["Kokoro"] = {
            "installed": None,
            "type": "python module",
            "path": None,
        }

        report = generate_terminal_report(self.data)

        self.assertIn("Kokoro", report)
        self.assertIn("INSPECTION ERROR", report)

    def test_terminal_report_handles_missing_ram_value(self):
        del self.data["hardware"]["ram"]["available_bytes"]

        report = generate_terminal_report(self.data)

        self.assertIn("RAM Available: UNKNOWN", report)

    def test_terminal_report_handles_missing_storage_value(self):
        del self.data["hardware"]["storage"]["available_bytes"]

        report = generate_terminal_report(self.data)

        self.assertIn("Storage Free : UNKNOWN", report)

    def test_terminal_report_handles_missing_cpu_threads(self):
        del self.data["hardware"]["cpu_threads"]

        report = generate_terminal_report(self.data)

        self.assertIn("CPU Threads  : UNKNOWN", report)

    def test_terminal_report_handles_missing_architecture(self):
        del self.data["hardware"]["architecture"]

        report = generate_terminal_report(self.data)

        self.assertIn("Architecture : UNKNOWN", report)

    def test_terminal_report_handles_missing_python_version(self):
        del self.data["software"]["python_version"]

        report = generate_terminal_report(self.data)

        self.assertIn("Python           : UNKNOWN", report)

    def test_terminal_report_handles_missing_operating_system(self):
        del self.data["software"]["operating_system"]

        report = generate_terminal_report(self.data)

        self.assertIn("Operating System : UNKNOWN", report)

    def test_terminal_report_handles_missing_termux_status(self):
        del self.data["software"]["is_termux"]

        report = generate_terminal_report(self.data)

        self.assertIn("Termux           : UNKNOWN", report)

    def test_terminal_report_handles_missing_commands(self):
        del self.data["software"]["commands"]

        report = generate_terminal_report(self.data)

        self.assertIn("Development tools: UNKNOWN", report)

    def test_terminal_report_handles_missing_dependencies(self):
        del self.data["dependencies"]

        report = generate_terminal_report(self.data)

        self.assertIn("PYTHON DEPENDENCIES", report)
        self.assertIn("Dependency information: UNKNOWN", report)

    def test_terminal_report_handles_missing_ai_readiness(self):
        del self.data["ai_readiness"]

        report = generate_terminal_report(self.data)

        self.assertIn("Readiness: UNKNOWN", report)

    def test_terminal_report_contains_readiness_status(self):
        report = generate_terminal_report(self.data)

        self.assertIn("LIMITED", report)
        self.assertIn("NOT READY", report)
        self.assertIn("UNKNOWN", report)

    def test_export_creates_txt_and_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = export_reports(self.data, temp_dir)

            self.assertTrue(paths["txt"])
            self.assertTrue(paths["json"])

            with open(paths["txt"], encoding="utf-8") as file:
                txt_content = file.read()

            with open(paths["json"], encoding="utf-8") as file:
                json_data = json.load(file)

            self.assertIn("TERMUX SYSTEM AUDITOR", txt_content)
            self.assertEqual(json_data, self.data)

    def test_repeated_exports_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("reports.generator.datetime", FixedDateTime):
                first = export_reports(self.data, temp_dir)
                second = export_reports(self.data, temp_dir)

            self.assertNotEqual(first["txt"], second["txt"])
            self.assertNotEqual(first["json"], second["json"])

    def test_export_cleans_up_after_write_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_write = Path.write_text
            write_count = 0

            def simulate_failure(path, *args, **kwargs):
                nonlocal write_count
                write_count += 1

                if write_count == 2:
                    raise OSError("Simulated JSON write failure")

                return original_write(path, *args, **kwargs)

            with (
                patch(
                    "pathlib.Path.write_text",
                    new=simulate_failure,
                ),
                self.assertRaises(OSError),
            ):
                export_reports(self.data, temp_dir)

            remaining_files = list(Path(temp_dir).glob("audit-*"))
            self.assertEqual(remaining_files, [])


if __name__ == "__main__":
    unittest.main()
