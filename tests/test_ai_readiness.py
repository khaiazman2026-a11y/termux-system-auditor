"""Tests for local AI readiness assessments."""

import unittest
from unittest.mock import patch

from ai.image import assess_image_readiness, find_image_models
from ai.llm import assess_llm_readiness, find_gguf_models
from ai.tts import assess_tts_readiness, find_tts_engines


class TestLLMReadiness(unittest.TestCase):
    def setUp(self):
        self.engines = {
            "llama-server": {"installed": True},
            "llama-cli": {"installed": True},
        }
        self.models = [{"name": "model.gguf", "size_bytes": 1024}]

    def test_missing_engine(self):
        engines = {
            "llama-server": {"installed": False},
            "llama-cli": {"installed": False},
        }
        result = assess_llm_readiness(engines, self.models, 4096)
        self.assertEqual(result["status"], "NOT READY")

    def test_missing_model(self):
        result = assess_llm_readiness(self.engines, [], 4096)
        self.assertEqual(result["status"], "UNKNOWN")

    def test_unknown_available_ram(self):
        result = assess_llm_readiness(self.engines, self.models, None)
        self.assertEqual(result["status"], "UNKNOWN")

    def test_model_larger_than_available_ram(self):
        result = assess_llm_readiness(self.engines, self.models, 512)
        self.assertEqual(result["status"], "LIMITED")

    def test_model_smaller_than_available_ram(self):
        result = assess_llm_readiness(self.engines, self.models, 4096)
        self.assertEqual(result["status"], "LIMITED")


class TestGGUFModelDiscovery(unittest.TestCase):
    def test_inaccessible_model_directory(self):
        with (
            patch("pathlib.Path.is_dir", return_value=True),
            patch(
                "pathlib.Path.iterdir",
                side_effect=PermissionError("Access denied"),
            ),
        ):
            models = find_gguf_models("/restricted/models")

        self.assertIsNone(models)

    def test_missing_model_directory(self):
        with patch("pathlib.Path.is_dir", return_value=False):
            models = find_gguf_models("/missing/models")

        self.assertIsNone(models)


class TestTTSEngineDiscovery(unittest.TestCase):
    def test_python_module_inspection_error(self):
        with patch(
            "ai.tts.importlib.util.find_spec",
            side_effect=OSError("Inspection failed"),
        ):
            engines = find_tts_engines()

        self.assertIsNone(engines["Pocket TTS"]["installed"])


class TestTTSReadiness(unittest.TestCase):
    def test_no_engine(self):
        engines = {
            "Pocket TTS": {"installed": False},
            "Piper": {"installed": False},
        }
        result = assess_tts_readiness(engines)
        self.assertEqual(result["status"], "NOT READY")

    def test_engine_detected(self):
        engines = {
            "Pocket TTS": {"installed": True},
            "Piper": {"installed": False},
        }
        result = assess_tts_readiness(engines)
        self.assertEqual(result["status"], "LIMITED")


class TestImageModelDiscovery(unittest.TestCase):
    def test_inaccessible_model_directory(self):
        with (
            patch("pathlib.Path.is_dir", return_value=True),
            patch(
                "pathlib.Path.iterdir",
                side_effect=PermissionError("Access denied"),
            ),
        ):
            models = find_image_models("/restricted/models")

        self.assertIsNone(models)

    def test_missing_model_directory(self):
        with patch("pathlib.Path.is_dir", return_value=False):
            models = find_image_models("/missing/models")

        self.assertIsNone(models)


class TestImageReadiness(unittest.TestCase):
    def setUp(self):
        self.engines = {
            "sd-cli": {"installed": True},
            "sd-server": {"installed": True},
        }
        self.models = [{"name": "sdxs.safetensors", "size_bytes": 1024}]

    def test_missing_engine(self):
        engines = {
            "sd-cli": {"installed": False},
            "sd-server": {"installed": False},
        }
        result = assess_image_readiness(engines, self.models, 4096)
        self.assertEqual(result["status"], "NOT READY")

    def test_missing_model(self):
        result = assess_image_readiness(self.engines, [], 4096)
        self.assertEqual(result["status"], "UNKNOWN")

    def test_unknown_available_ram(self):
        result = assess_image_readiness(self.engines, self.models, None)
        self.assertEqual(result["status"], "UNKNOWN")

    def test_model_larger_than_available_ram(self):
        result = assess_image_readiness(self.engines, self.models, 512)
        self.assertEqual(result["status"], "LIMITED")

    def test_model_smaller_than_available_ram(self):
        result = assess_image_readiness(self.engines, self.models, 4096)
        self.assertEqual(result["status"], "LIMITED")


if __name__ == "__main__":
    unittest.main()
