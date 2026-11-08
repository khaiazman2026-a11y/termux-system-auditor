"""Software environment inspector for Termux System Auditor."""

import os
import platform
import shutil
import subprocess
import sys


def get_command_info(command):
    """Return availability, path and version of a command."""
    path = shutil.which(command)

    if path is None:
        return {
            "installed": False,
            "path": None,
            "version": None,
        }

    version = None

    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )

        output = result.stdout.strip() or result.stderr.strip()

        if output:
            version = output.splitlines()[0]

    except (OSError, subprocess.TimeoutExpired):
        pass

    return {
        "installed": True,
        "path": path,
        "version": version,
    }


def get_software_info():
    """Collect software environment information."""

    commands = [
        "bash",
        "curl",
        "git",
        "cmake",
        "clang",
        "make",
        "pkg-config",
    ]

    software = {
        "operating_system": platform.system(),
        "kernel": platform.release(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "is_termux": bool(
            os.environ.get("PREFIX", "").endswith("/com.termux/files/usr")
        ),
        "termux_prefix": os.environ.get("PREFIX"),
        "commands": {},
    }

    for command in commands:
        software["commands"][command] = get_command_info(command)

    return software
