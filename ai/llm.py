"""Local LLM readiness inspector."""

import shutil
from pathlib import Path

from core.hardware import get_hardware_info


def find_llama_engine():
    """Find llama.cpp executables in PATH and known build locations."""

    names = ("llama-server", "llama-cli")

    build_dirs = [
        Path.home() / "src/llama.cpp/build/bin",
        Path.home() / "llama.cpp/build/bin",
    ]

    engines = {}

    for name in names:
        found = shutil.which(name)

        if found is None:
            for directory in build_dirs:
                candidate = directory / name

                if candidate.is_file():
                    found = str(candidate)
                    break

        engines[name] = {
            "installed": found is not None,
            "path": found,
        }

    return engines


def find_gguf_models(model_dir=None):
    """Find GGUF model files in the selected directory."""

    directory = Path(model_dir) if model_dir else Path.home() / "models"

    models = []

    try:
        if not directory.is_dir():
            return None
    except OSError:
        return None

    try:
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() == ".gguf":
                try:
                    models.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "size_bytes": item.stat().st_size,
                        }
                    )
                except OSError:
                    continue
    except OSError:
        return None

    return models


def assess_llm_readiness(engines, models, available_ram):
    """Provide a conservative preliminary readiness assessment."""

    engine_available = any(engine["installed"] for engine in engines.values())

    if not engine_available:
        return {
            "status": "NOT READY",
            "reason": "No llama.cpp executable was detected.",
        }

    if models is None:
        return {
            "status": "UNKNOWN",
            "reason": "The model directory could not be inspected.",
        }

    if not models:
        return {
            "status": "UNKNOWN",
            "reason": "No GGUF model was detected in the model directory.",
        }

    if available_ram is None:
        return {
            "status": "UNKNOWN",
            "reason": "Available RAM could not be determined.",
        }

    largest_model = max(models, key=lambda model: model["size_bytes"])

    if largest_model["size_bytes"] >= available_ram:
        reason = (
            "The model file is at least as large as available RAM. "
            "Actual memory requirements depend on runtime behavior, "
            "memory mapping, and offloading; they have not been tested."
        )
    else:
        reason = (
            "A llama.cpp engine and GGUF model were detected. "
            "Actual inference compatibility and memory use have not been tested."
        )

    return {
        "status": "LIMITED",
        "reason": reason,
    }


def get_llm_info(model_dir=None):
    """Collect local LLM environment information."""

    hardware = get_hardware_info()
    engines = find_llama_engine()

    discovered_models = find_gguf_models(model_dir)
    models = discovered_models if discovered_models is not None else []

    available_ram = hardware["ram"]["available_bytes"]

    return {
        "engines": engines,
        "model_directory": str(
            Path(model_dir) if model_dir else Path.home() / "models"
        ),
        "models": models,
        "model_count": len(models),
        "available_ram_bytes": available_ram,
        "readiness": assess_llm_readiness(
            engines,
            discovered_models,
            available_ram,
        ),
    }
