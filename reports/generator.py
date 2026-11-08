"""Report generator for Termux System Auditor."""

import json
from datetime import datetime, timezone
from pathlib import Path

from ai.image import get_image_info
from ai.llm import get_llm_info
from ai.tts import get_tts_info
from core.dependencies import get_dependency_info
from core.hardware import format_bytes, get_hardware_info
from core.software import get_software_info


def generate_audit():
    """Collect all system and AI readiness information."""

    return {
        "audit_time": datetime.now(timezone.utc).isoformat(),
        "hardware": get_hardware_info(),
        "software": get_software_info(),
        "dependencies": get_dependency_info(),
        "ai_readiness": {
            "llm": get_llm_info(),
            "tts": get_tts_info(),
            "image_generation": get_image_info(),
        },
    }


def generate_terminal_report(data):
    """Format audit information for terminal display."""

    hardware = data["hardware"]
    software = data["software"]

    lines = [
        "=" * 45,
        "         TERMUX SYSTEM AUDITOR",
        "=" * 45,
        "",
        "HARDWARE",
        "-" * 45,
        f"Architecture : {hardware['architecture']}",
        f"CPU Threads  : {hardware['cpu_threads']}",
        f"RAM Total    : {format_bytes(hardware['ram']['total_bytes'])}",
        f"RAM Available: {format_bytes(hardware['ram']['available_bytes'])}",
        f"Storage Free : {format_bytes(hardware['storage']['available_bytes'])}",
        "",
        "SOFTWARE",
        "-" * 45,
        f"Operating System : {software['operating_system']}",
        f"Python           : {software['python_version']}",
        f"Termux           : {software['is_termux']}",
        "",
        "DEVELOPMENT TOOLS",
        "-" * 45,
    ]

    for name, info in software["commands"].items():
        status = "INSTALLED" if info["installed"] else "NOT FOUND"
        lines.append(f"{name:15} {status}")

    lines.extend(
        [
            "",
            "PYTHON DEPENDENCIES",
            "-" * 45,
        ]
    )

    for name, info in data["dependencies"].items():
        status = "INSTALLED" if info["installed"] else "NOT FOUND"
        version = info["version"] or "-"
        lines.append(f"{name:15} {status:12} {version}")

    ai = data["ai_readiness"]

    for section, title in (
        ("llm", "LOCAL LLM"),
        ("tts", "LOCAL TEXT-TO-SPEECH"),
        ("image_generation", "IMAGE GENERATION"),
    ):
        result = ai[section]

        lines.extend(
            [
                "",
                title,
                "-" * 45,
            ]
        )

        for name, info in result["engines"].items():
            status = "FOUND" if info["installed"] else "NOT FOUND"
            lines.append(f"{name:22} {status}")

        if "models" in result:
            lines.append(f"Models detected: {result['model_count']}")

            for model in result["models"]:
                lines.append(f"  {model['name']} ({format_bytes(model['size_bytes'])})")

        lines.extend(
            [
                f"Readiness: {result['readiness']['status']}",
                f"Reason: {result['readiness']['reason']}",
            ]
        )

    lines.extend(
        [
            "",
            f"Audit time: {data['audit_time']}",
            "=" * 45,
        ]
    )

    return "\n".join(lines)


def export_reports(data, output_dir="reports/output"):
    """Export audit data into TXT and JSON files."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    txt_path = directory / f"audit-{timestamp}.txt"
    json_path = directory / f"audit-{timestamp}.json"

    counter = 1

    while txt_path.exists() or json_path.exists():
        suffix = f"-{counter}"
        txt_path = directory / f"audit-{timestamp}{suffix}.txt"
        json_path = directory / f"audit-{timestamp}{suffix}.json"
        counter += 1

    txt_content = generate_terminal_report(data)
    json_content = json.dumps(data, indent=2, ensure_ascii=False)

    try:
        txt_path.write_text(
            txt_content,
            encoding="utf-8",
        )

        json_path.write_text(
            json_content,
            encoding="utf-8",
        )

    except OSError:
        for path in (txt_path, json_path):
            try:
                path.unlink()
            except FileNotFoundError:
                pass

        raise

    return {
        "txt": str(txt_path),
        "json": str(json_path),
    }
