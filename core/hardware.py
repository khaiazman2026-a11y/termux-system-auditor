"""Hardware information collector for Termux System Auditor."""

import os
import platform
import shutil
from pathlib import Path


def format_bytes(value):
    """Convert bytes into a human-readable string."""
    if value is None:
        return "UNKNOWN"

    size = float(value)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024

    return "UNKNOWN"


def get_memory_info():
    """Read total and available RAM from /proc/meminfo."""
    memory = {}

    with open("/proc/meminfo", "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split()

            if len(parts) >= 2:
                key = parts[0].rstrip(":")
                if key in ("MemTotal", "MemAvailable"):
                    memory[key] = int(parts[1]) * 1024

    return {
        "total_bytes": memory.get("MemTotal"),
        "available_bytes": memory.get("MemAvailable"),
    }


def get_storage_info(path=None):
    """Inspect storage capacity for a selected directory."""
    target = Path(path) if path is not None else Path.home()

    try:
        usage = shutil.disk_usage(target)

        return {
            "path": str(target),
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "available_bytes": usage.free,
        }

    except OSError:
        return {
            "path": str(target),
            "total_bytes": None,
            "used_bytes": None,
            "available_bytes": None,
        }


def get_hardware_info(storage_path=None):
    """Collect hardware information and return structured data."""
    try:
        memory = get_memory_info()
    except (OSError, ValueError):
        memory = {
            "total_bytes": None,
            "available_bytes": None,
        }

    return {
        "architecture": platform.machine() or "UNKNOWN",
        "cpu_threads": os.cpu_count(),
        "ram": memory,
        "storage": get_storage_info(storage_path),
    }
