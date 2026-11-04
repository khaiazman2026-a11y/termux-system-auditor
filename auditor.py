"""Main entry point for Termux System Auditor."""

from reports.generator import (
    generate_audit,
    generate_terminal_report,
    export_reports,
)


def main():
    print("Running Termux System Audit...\n")

    data = generate_audit()

    print(generate_terminal_report(data))

    files = export_reports(data)

    print("\n=== EXPORTED REPORTS ===")
    print("TXT :", files["txt"])
    print("JSON:", files["json"])


if __name__ == "__main__":
    main()
