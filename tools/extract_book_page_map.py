"""Extract rendered heading page numbers for the static linked Word contents table."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SPECIAL_HEADINGS = (
    "Appendices",
    "Practice Casebook — Seventy-Two Worked Assignments",
    "Technical Workbook — End-to-End Python Patterns",
    "Numerical Examples — Calculation, Interpretation, and Audit",
    "Credit Risk Policy Playbook",
    "Review and Viva Questions with Instructor Notes",
    "Technical and Governance Glossary",
)


def extract(pdf: Path) -> dict[str, int]:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    page_map: dict[str, int] = {}
    for page_number, page in enumerate(completed.stdout.split("\f"), start=1):
        for match in re.finditer(r"(?m)^\s*Chapter\s+(\d+)\s+[—-]", page):
            page_map.setdefault(f"Chapter {int(match.group(1))}", page_number)
        for heading in SPECIAL_HEADINGS:
            if re.search(rf"(?m)^\s*{re.escape(heading)}\s*$", page):
                page_map.setdefault(heading, page_number)
    missing = [
        f"Chapter {number}" for number in range(1, 73) if f"Chapter {number}" not in page_map
    ]
    if missing:
        raise RuntimeError(f"Missing rendered chapter headings: {missing}")
    return page_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, default=Path("book/page_map.json"))
    arguments = parser.parse_args()
    page_map = extract(arguments.pdf.resolve())
    arguments.output.write_text(
        json.dumps(page_map, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(page_map)} heading pages to {arguments.output}")


if __name__ == "__main__":
    main()
