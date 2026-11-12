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
        f"Architecture : {hardware.get('architecture', 'UNKNOWN')}",
        f"CPU Threads  : {hardware.get('cpu_threads', 'UNKNOWN')}",
        f"RAM Total    : {format_bytes(hardware['ram']['total_bytes'])}",
        f"RAM Available: {format_bytes(hardware['ram'].get('available_bytes'))}",
        f"Storage Free : {format_bytes(hardware['storage'].get('available_bytes'))}",
        "",
        "SOFTWARE",
        "-" * 45,
        f"Operating System : {software.get('operating_system', 'UNKNOWN')}",
        f"Python           : {software.get('python_version', 'UNKNOWN')}",
        f"Termux           : {software.get('is_termux', 'UNKNOWN')}",
        "",
        "DEVELOPMENT TOOLS",
        "-" * 45,
    ]

    commands = software.get("commands")

    if commands is None:
        lines.append("Development tools: UNKNOWN")
    else:
        for name, info in commands.items():
            status = "INSTALLED" if info["installed"] else "NOT FOUND"
            lines.append(f"{name:15} {status}")

    lines.extend(
        [
            "",
            "PYTHON DEPENDENCIES",
            "-" * 45,
        ]
    )

    dependencies = data.get("dependencies")

    if dependencies is None:
        lines.append("Dependency information: UNKNOWN")
    else:
        for name, info in dependencies.items():
            if info.get("inspection_status") == "ERROR":
                status = "INSPECTION ERROR"
            elif info["installed"] is True:
                status = "INSTALLED"
            elif info["installed"] is False:
                status = "NOT FOUND"
            else:
                status = "UNKNOWN"

            version = info.get("version") or "-"
            lines.append(f"{name:15} {status:16} {version}")
    ai = data.get("ai_readiness") or {}

    for section, title in (
        ("llm", "LOCAL LLM"),
        ("tts", "LOCAL TEXT-TO-SPEECH"),
        ("image_generation", "IMAGE GENERATION"),
    ):
        result = ai.get(section)

        if result is None:
            lines.extend(
                [
                    "",
                    title,
                    "-" * 45,
                    "Readiness: UNKNOWN",
                    "Reason: AI readiness data unavailable.",
                ]
            )
            continue
        lines.extend(
            [
                "",
                title,
                "-" * 45,
            ]
        )

        engines = result.get("engines") or {}

        for name, info in engines.items():
            if info.get("installed") is True:
                status = "FOUND"
            elif info.get("installed") is False:
                status = "NOT FOUND"
            else:
                status = "INSPECTION ERROR"

            lines.append(f"{name:22} {status}")

        if "models" in result:
            models = result.get("models") or []
            model_count = result.get("model_count", len(models))
            lines.append(f"Models detected: {model_count}")

            for model in models:
                name = model.get("name", "UNKNOWN")
                size = format_bytes(model.get("size_bytes"))
                lines.append(f"  {name} ({size})")

        readiness = result.get("readiness") or {}
        lines.extend(
            [
                f"Readiness: {readiness.get('status', 'UNKNOWN')}",
                f"Reason: {readiness.get('reason', 'Readiness information unavailable.')}",
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
