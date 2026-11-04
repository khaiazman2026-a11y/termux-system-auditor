# Termux System Auditor

A lightweight, offline-first system diagnostic tool for Android devices running Termux.

## Overview

Termux System Auditor collects hardware and software information from an Android device and evaluates its readiness for local AI workloads.

The project is designed for Termux users, developers, and hobbyists who want to understand their device capabilities without relying on cloud services.

## Features

### Core System Audit

- CPU architecture detection
- CPU thread count
- RAM information
- Storage capacity and availability
- Android and Termux environment detection
- Python and system utility detection
- Python dependency checking

Local AI Readiness

- Local LLM readiness evaluation
- Local TTS readiness evaluation
- Local image-generation readiness evaluation
- Resource suitability estimation
- Missing dependency detection

Reporting

- Terminal output
- TXT report export
- JSON report export

Requirements

- Android device
- Termux
- Python 3
- ARM64 / aarch64 (initial development target)

Installation

Installation instructions will be provided during development.

Usage

Usage instructions will be provided when the first working version is released.

Project Status

Currently under development.

Target release: v0.1.0

Design Principles

- Offline-first
- Read-only diagnostics
- No root access required
- Minimal external dependencies
- Transparent hardware and resource assessments

License

MIT License. See the LICENSE file for details.
