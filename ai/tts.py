"""Local TTS readiness inspector."""

import importlib.util
import shutil

COMMANDS = {
    "pocket-tts": "Pocket TTS",
    "piper": "Piper",
    "espeak-ng": "eSpeak NG",
    "espeak": "eSpeak",
    "termux-tts-speak": "Termux Android TTS",
}

PYTHON_MODULES = {
    "pocket_tts": "Pocket TTS",
    "TTS": "Coqui TTS",
    "kokoro": "Kokoro",
}


def find_tts_engines():
    """Detect available TTS commands and Python modules."""

    engines = {}

    for command, name in COMMANDS.items():
        path = shutil.which(command)

        engines[name] = {
            "installed": path is not None,
            "type": "command",
            "path": path,
        }

    for module, name in PYTHON_MODULES.items():
        try:
            available = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            available = False

        engines[name] = {
            "installed": available,
            "type": "python module",
            "path": None,
        }

    return engines


def assess_tts_readiness(engines):
    """Estimate TTS readiness without claiming a voice test."""

    detected = [name for name, info in engines.items() if info["installed"]]

    if not detected:
        return {
            "status": "NOT READY",
            "reason": "No supported TTS engine was detected.",
        }

    return {
        "status": "LIMITED",
        "reason": (
            "At least one TTS engine was detected, but voice availability, "
            "model files, and offline operation have not been tested."
        ),
        "detected_engines": detected,
    }


def get_tts_info():
    """Collect local TTS environment information."""

    engines = find_tts_engines()

    return {
        "engines": engines,
        "engine_count": sum(1 for info in engines.values() if info["installed"]),
        "readiness": assess_tts_readiness(engines),
    }
