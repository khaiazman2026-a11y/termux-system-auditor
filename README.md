# Termux System Auditor

A lightweight, offline-first diagnostic tool for Android devices running Termux.

## Overview

Termux System Auditor collects hardware and software information and evaluates device readiness for local AI workloads.

It is designed to work locally without root access, internet connectivity, or third-party dependencies for the auditor itself.

## Features

### Core System Audit

- CPU architecture and logical thread detection
- Total and available RAM
- Storage capacity and available space
- Android and Termux environment detection
- Python and system utility detection
- Python dependency checking

### Local AI Readiness

- Local LLM engine and GGUF model detection
- Local TTS engine detection
- Local image-generation engine and model detection
- Resource suitability estimation
- Missing dependency detection

### Reports

- Terminal report
- TXT report export
- JSON report export

## Requirements

- Android device running Termux
- Python 3.10 or later
- No root access required
- No third-party Python dependencies required by the auditor

ARM64 / aarch64 is the initial development target.

## Installation

Clone the repository:

```bash
git clone https://github.com/khaiazman2026-a11y/termux-system-auditor.git
cd termux-system-auditor
````

### Usage

Run the auditor:

```bash
python auditor.py
```

Reports are generated in:

```text
reports/output/
```

### Tests

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Check Python syntax:

```bash
python -m py_compile auditor.py core/*.py ai/*.py reports/*.py
```

### Readiness Status

The auditor uses four readiness categories:

| Status    | Meaning                                                |
| --------- | ------------------------------------------------------ |
| READY     | Requirements appear to be satisfied                    |
| LIMITED   | Some requirements are detected, but limitations remain |
| NOT READY | A required component is missing                        |
| UNKNOWN   | Available information is insufficient                  |

Readiness assessments are estimates based on detected information. They are not proof that a model can run successfully.

Model file size alone does not determine runtime RAM requirements. Actual compatibility, memory usage, and performance require runtime testing.

### Design Principles

* Offline-first

* Read-only system inspection

* No root requirement

* No automatic package installation

* Standard-library-first implementation

* Explicit distinction between detected facts and estimated readiness

### Project Roadmap

* Phase 0: Project specification

* Phase 1: GitHub foundation

* Phase 2: Core inspection and reporting

* Phase 3: Local AI readiness assessment

* Phase 4: Report improvements and expanded testing

* Phase 5: Documentation, release preparation, and validation

### License

MIT License. See LICENSE.

