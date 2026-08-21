"""Enforce the construction-first learning architecture."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GUIDED = ROOT / "book" / "guided_labs"
MANUSCRIPT = ROOT / "book" / "full_manuscript"
SCRIPTS = ROOT / "examples" / "from_scratch"

PROJECT_IMPORT = re.compile(r"(?:from|import)\s+creditriskbook\b")
FOUNDATION_DATA_SCIENCE_IMPORT = re.compile(
    r"(?:from|import)\s+(?:numpy|pandas|scipy|sklearn|xgboost)\b"
)


def main() -> None:
    structure = json.loads((ROOT / "book" / "structure.json").read_text(encoding="utf-8"))
    chapters = [chapter for part in structure["parts"] for chapter in part["chapters"]]
    chapter_numbers = [int(chapter["number"]) for chapter in chapters]
    assert chapter_numbers == list(range(1, len(chapters) + 1))

    early_manuscript = "\n".join(
        (MANUSCRIPT / name).read_text(encoding="utf-8")
        for name in (
            "01_part_i_foundations.md",
            "02_part_ii_products_policy.md",
            "03_part_iii_regulation_accounting.md",
            "04_part_iv_data_quality.md",
        )
    )
    assert not PROJECT_IMPORT.search(early_manuscript), (
        "Chapters 1-24 must show complete standalone code before project-library imports"
    )

    for number in chapter_numbers:
        lab = (GUIDED / f"chapter_{number:02d}.md").read_text(encoding="utf-8")
        assert "```python" in lab, f"Chapter {number} has no tagged Python window"
        assert "```output" in lab, f"Chapter {number} has no executed-output window"
        if number <= 24:
            assert not PROJECT_IMPORT.search(lab), f"Chapter {number} imports the project library"

    scripts = sorted(SCRIPTS.glob("chapter_*.py"))
    assert len(scripts) == 24, f"Expected 24 standalone scripts, found {len(scripts)}"
    for path in scripts:
        text = path.read_text(encoding="utf-8")
        assert not PROJECT_IMPORT.search(text), f"Standalone script imports the library: {path}"
        chapter_number = int(path.name.split("_")[1])
        if chapter_number <= 6:
            assert not FOUNDATION_DATA_SCIENCE_IMPORT.search(text), (
                f"Chapter {chapter_number} must begin with built-in Python or the standard library"
            )
            assert len(text.splitlines()) <= 45, (
                f"Chapter {chapter_number} exceeds the introductory code-size limit"
            )
        completed = subprocess.run(
            [sys.executable, str(path)], cwd=ROOT, text=True, capture_output=True, timeout=60
        )
        if completed.returncode:
            raise RuntimeError(f"{path} failed\n{completed.stdout}\n{completed.stderr}")
        assert completed.stdout.strip(), f"{path} must show an inspectable output"

    registry = yaml.safe_load((ROOT / "data" / "dataset_registry.yml").read_text(encoding="utf-8"))
    assert len(registry["datasets"]) >= 30, "The exercise catalogue requires at least 30 sources"

    titles = " ".join(chapter["title"].lower() for chapter in chapters[-6:])
    for term in ("nlp", "document", "llm", "agent", "retrieval", "evaluation"):
        assert term in titles, f"The final learning path must explicitly cover {term}"

    print(
        f"Pedagogy audit passed: {len(chapters)} chapters, 24 standalone scripts, "
        f"{len(registry['datasets'])} dataset records."
    )


if __name__ == "__main__":
    main()
