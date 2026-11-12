"""Tests for software environment inspection."""

import subprocess
import unittest
from unittest.mock import Mock, patch

from core.software import get_command_info, get_software_info


class TestCommandInfo(unittest.TestCase):
    @patch("core.software.shutil.which", return_value=None)
    def test_missing_command(self, mock_which):
        result = get_command_info("missing-command")

        self.assertFalse(result["installed"])
        self.assertIsNone(result["path"])
        self.assertIsNone(result["version"])

    @patch("core.software.subprocess.run")
    @patch("core.software.shutil.which", return_value="/usr/bin/git")
    def test_detects_command_version(self, mock_which, mock_run):
        mock_run.return_value = Mock(
            stdout="git version 2.56.0\n",
            stderr="",
            returncode=0,
        )

        result = get_command_info("git")

        self.assertTrue(result["installed"])
        self.assertEqual(result["path"], "/usr/bin/git")
        self.assertEqual(result["version"], "git version 2.56.0")

    @patch(
        "core.software.subprocess.run",
        side_effect=subprocess.TimeoutExpired("git", 3),
    )
    @patch("core.software.shutil.which", return_value="/usr/bin/git")
    def test_timeout_returns_unknown_version(self, mock_which, mock_run):
        result = get_command_info("git")

        self.assertTrue(result["installed"])
        self.assertEqual(result["path"], "/usr/bin/git")
        self.assertIsNone(result["version"])

    @patch(
        "core.software.subprocess.run",
        side_effect=OSError("execution failed"),
    )
    @patch("core.software.shutil.which", return_value="/usr/bin/git")
    def test_execution_error_returns_unknown_version(self, mock_which, mock_run):
        result = get_command_info("git")

        self.assertTrue(result["installed"])
        self.assertEqual(result["path"], "/usr/bin/git")
        self.assertIsNone(result["version"])

    @patch("core.software.subprocess.run")
    @patch("core.software.shutil.which", return_value="/usr/bin/git")
    def test_nonzero_exit_code_returns_unknown_version(self, mock_which, mock_run):
        mock_run.return_value = Mock(
            stdout="",
            stderr="git: error",
            returncode=1,
        )

        result = get_command_info("git")

        self.assertTrue(result["installed"])
        self.assertIsNone(result["version"])

    @patch("core.software.subprocess.run")
    @patch("core.software.shutil.which", return_value="/usr/bin/git")
    def test_empty_output_returns_unknown_version(self, mock_which, mock_run):
        mock_run.return_value = Mock(
            stdout="",
            stderr="",
            returncode=0,
        )

        result = get_command_info("git")

        self.assertTrue(result["installed"])
        self.assertIsNone(result["version"])


class TestSoftwareInfo(unittest.TestCase):
    @patch("core.software.get_command_info")
    def test_collects_environment_metadata(self, mock_command):
        mock_command.return_value = {
            "installed": True,
            "path": "/usr/bin/git",
            "version": "git version 2.56.0",
        }

        result = get_software_info()

        self.assertIn("operating_system", result)
        self.assertIn("kernel", result)
        self.assertIn("python_version", result)
        self.assertIn("python_executable", result)
        self.assertIn("is_termux", result)
        self.assertIn("termux_prefix", result)
        self.assertIn("commands", result)

    @patch("core.software.get_command_info")
    def test_checks_all_expected_commands(self, mock_command):
        mock_command.return_value = {
            "installed": False,
            "path": None,
            "version": None,
        }

        result = get_software_info()

        expected = {
            "bash",
            "curl",
            "git",
            "cmake",
            "clang",
            "make",
            "pkg-config",
        }

        self.assertEqual(set(result["commands"]), expected)
        self.assertEqual(mock_command.call_count, len(expected))


if __name__ == "__main__":
    unittest.main()
