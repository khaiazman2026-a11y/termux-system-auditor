import unittest
from unittest.mock import patch

from core.dependencies import check_dependency


class TestCheckDependency(unittest.TestCase):
    @patch("core.dependencies.importlib.util.find_spec")
    def test_detects_installed_module(self, mock_find_spec):
        mock_find_spec.return_value = object()

        with patch(
            "core.dependencies.importlib.metadata.version",
            return_value="1.0.0",
        ):
            result = check_dependency("example")

        self.assertTrue(result["installed"])
        self.assertEqual(result["version"], "1.0.0")

    @patch("core.dependencies.importlib.util.find_spec")
    def test_detects_missing_module(self, mock_find_spec):
        mock_find_spec.return_value = None

        result = check_dependency("example")

        self.assertFalse(result["installed"])
        self.assertIsNone(result["version"])

    @patch("core.dependencies.importlib.util.find_spec")
    def test_inspection_error_is_distinguished(self, mock_find_spec):
        mock_find_spec.side_effect = ImportError("inspection failed")

        result = check_dependency("example")

        self.assertIsNone(result["installed"])
        self.assertIsNone(result["version"])

    @patch("core.dependencies.importlib.util.find_spec")
    def test_missing_package_metadata_keeps_module_installed(self, mock_find_spec):
        mock_find_spec.return_value = object()

        with patch(
            "core.dependencies.importlib.metadata.version",
            side_effect=__import__(
                "importlib.metadata", fromlist=["PackageNotFoundError"]
            ).PackageNotFoundError,
        ):
            result = check_dependency("example")

        self.assertTrue(result["installed"])
        self.assertEqual(result["version"], "VERSION UNKNOWN")


if __name__ == "__main__":
    unittest.main()
