"""Local image-generation readiness inspector."""

import shutil
from pathlib import Path

from core.hardware import get_hardware_info

ENGINE_NAMES = ("sd-cli", "sd-server")

BUILD_DIRS = (
    Path.home() / "src/stable-diffusion.cpp/build/bin",
    Path.home() / "stable-diffusion.cpp/build/bin",
    Path.home() / "sd.cpp/build/bin",
)

MODEL_EXTENSIONS = {
    ".safetensors",
    ".ckpt",
    ".pt",
    ".pth",
}


def find_image_engines():
    """Find Stable Diffusion executables."""

    engines = {}

    for name in ENGINE_NAMES:
        found = shutil.which(name)

        if found is None:
            for directory in BUILD_DIRS:
                candidate = directory / name

                if candidate.is_file():
                    found = str(candidate)
                    break

        engines[name] = {
            "installed": found is not None,
            "path": found,
        }

    return engines


def find_image_models(model_dir=None):
    """Find supported image-generation model files."""

    directory = Path(model_dir) if model_dir else Path.home() / "models"
    models = []

    if not directory.is_dir():
        return models

    try:
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in MODEL_EXTENSIONS:
                try:
                    models.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "format": item.suffix.lower(),
                            "size_bytes": item.stat().st_size,
                        }
                    )
                except OSError:
                    continue
    except OSError:
        pass

    return models


def assess_image_readiness(engines, models, available_ram):
    """Estimate readiness without performing image generation."""

    engine_available = any(engine["installed"] for engine in engines.values())

    if not engine_available:
        return {
            "status": "NOT READY",
            "reason": "No supported image-generation executable was detected.",
        }

    if not models:
        return {
            "status": "UNKNOWN",
            "reason": "No supported image-generation model was detected.",
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
            "Actual memory requirements depend on runtime behavior "
            "and have not been tested."
        )
    else:
        reason = (
            "An engine and model were detected, but model compatibility, "
            "runtime memory requirements, and actual generation have "
            "not been tested."
        )

    return {"status": "LIMITED", "reason": reason}


def get_image_info(model_dir=None):
    """Collect local image-generation environment information."""

    hardware = get_hardware_info()
    engines = find_image_engines()
    models = find_image_models(model_dir)

    available_ram = hardware["ram"]["available_bytes"]

    return {
        "engines": engines,
        "model_directory": str(
            Path(model_dir) if model_dir else Path.home() / "models"
        ),
        "models": models,
        "model_count": len(models),
        "available_ram_bytes": available_ram,
        "readiness": assess_image_readiness(
            engines,
            models,
            available_ram,
        ),
    }
