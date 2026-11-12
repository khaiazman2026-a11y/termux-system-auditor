"""Tests for hardware information collection."""

import unittest
from types import SimpleNamespace
from unittest.mock import mock_open, patch

from core.hardware import get_memory_info, get_storage_info


class TestMemoryInfo(unittest.TestCase):
    def test_reads_memory_values(self):
        data = "MemTotal:       8000000 kB\nMemAvailable:   4000000 kB\n"

        with patch("builtins.open", mock_open(read_data=data)):
            result = get_memory_info()

        self.assertEqual(result["total_bytes"], 8000000 * 1024)
        self.assertEqual(result["available_bytes"], 4000000 * 1024)

    def test_malformed_value_does_not_crash(self):
        data = "MemTotal:       invalid kB\nMemAvailable:   4000000 kB\n"

        with patch("builtins.open", mock_open(read_data=data)):
            result = get_memory_info()

        self.assertIsNone(result["total_bytes"])
        self.assertEqual(result["available_bytes"], 4000000 * 1024)

    def test_missing_memory_field_returns_none(self):
        data = "MemTotal:       8000000 kB\n"

        with patch("builtins.open", mock_open(read_data=data)):
            result = get_memory_info()

        self.assertEqual(result["total_bytes"], 8000000 * 1024)
        self.assertIsNone(result["available_bytes"])

    def test_unreadable_meminfo_returns_none(self):
        with patch("builtins.open", side_effect=PermissionError):
            result = get_memory_info()

        self.assertIsNone(result["total_bytes"])
        self.assertIsNone(result["available_bytes"])


class TestStorageInfo(unittest.TestCase):
    @patch("core.hardware.shutil.disk_usage")
    def test_reads_storage_values(self, mock_disk_usage):
        mock_disk_usage.return_value = SimpleNamespace(
            total=10000,
            used=4000,
            free=6000,
        )

        result = get_storage_info("/tmp")

        self.assertEqual(result["path"], "/tmp")
        self.assertEqual(result["total_bytes"], 10000)
        self.assertEqual(result["used_bytes"], 4000)
        self.assertEqual(result["available_bytes"], 6000)

    @patch(
        "core.hardware.shutil.disk_usage",
        side_effect=PermissionError,
    )
    def test_inaccessible_storage_returns_none(self, mock_disk_usage):
        result = get_storage_info("/restricted")

        self.assertEqual(result["path"], "/restricted")
        self.assertIsNone(result["total_bytes"])
        self.assertIsNone(result["used_bytes"])
        self.assertIsNone(result["available_bytes"])


if __name__ == "__main__":
    unittest.main()
