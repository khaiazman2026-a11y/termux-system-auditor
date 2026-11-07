"""Report generator for Termux System Auditor."""

import json
from datetime import datetime, timezone
from pathlib import Path

from core.hardware import get_hardware_info, format_bytes
from core.software import get_software_info
from core.dependencies import get_dependency_info

from ai.llm import get_llm_info
from ai.tts import get_tts_info
from ai.image import get_image_info


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

    lines.extend([
        "",
        "PYTHON DEPENDENCIES",
        "-" * 45,
    ])

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

        lines.extend([
            "",
            title,
            "-" * 45,
        ])

        for name, info in result["engines"].items():
            status = "FOUND" if info["installed"] else "NOT FOUND"
            lines.append(f"{name:22} {status}")

        if "models" in result:
            lines.append(f"Models detected: {result['model_count']}")

            for model in result["models"]:
                lines.append(
                    f"  {model['name']} "
                    f"({format_bytes(model['size_bytes'])})"
                )

        lines.extend([
            f"Readiness: {result['readiness']['status']}",
            f"Reason: {result['readiness']['reason']}",
        ])

    lines.extend([
        "",
        f"Audit time: {data['audit_time']}",
        "=" * 45,
    ])

    return "\n".join(lines)


def export_reports(data, output_dir="reports/output"):
    """Export audit data into TXT and JSON files."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    txt_path = directory / f"audit-{timestamp}.txt"
    json_path = directory / f"audit-{timestamp}.json"

    txt_path.write_text(
        generate_terminal_report(data),
        encoding="utf-8",
    )

    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "txt": str(txt_path),
        "json": str(json_path),
    }
