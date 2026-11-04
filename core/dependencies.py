"""Python dependency checker for Termux System Auditor."""

import importlib.metadata
import importlib.util


DEFAULT_DEPENDENCIES = {
    "torch": "torch",
    "numpy": "numpy",
    "scipy": "scipy",
    "yaml": "PyYAML",
    "sentencepiece": "sentencepiece",
    "transformers": "transformers",
    "tokenizers": "tokenizers",
    "pocket_tts": "pocket-tts",
}


def check_dependency(module_name, package_name=None):
    """Check whether a Python module and its distribution are available."""

    if package_name is None:
        package_name = module_name

    try:
        available = importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        available = False

    version = None

    if available:
        try:
            version = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            version = "VERSION UNKNOWN"
        except Exception:
            version = "VERSION UNKNOWN"

    return {
        "module": module_name,
        "package": package_name,
        "installed": available,
        "version": version,
    }


def get_dependency_info(dependencies=None):
    """Check a list of Python dependencies."""

    if dependencies is None:
        dependencies = DEFAULT_DEPENDENCIES

    return {
        module: check_dependency(module, package)
        for module, package in dependencies.items()
    }
