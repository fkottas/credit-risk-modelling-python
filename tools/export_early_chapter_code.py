"""Export the exact standalone Chapter 1-24 code shown in the book."""

from __future__ import annotations

import json
import re
from pathlib import Path

from early_chapter_examples import EXAMPLES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples" / "from_scratch"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def main() -> None:
    structure = json.loads((ROOT / "book" / "structure.json").read_text(encoding="utf-8"))
    chapters = {
        int(chapter["number"]): chapter["title"]
        for part in structure["parts"]
        for chapter in part["chapters"]
        if int(chapter["number"]) <= 24
    }
    if set(chapters) != set(EXAMPLES):
        raise RuntimeError("Structure and standalone example numbers do not agree")
    OUT.mkdir(parents=True, exist_ok=True)
    expected = set()
    for number, title in chapters.items():
        path = OUT / f"chapter_{number:02d}_{slug(title)}.py"
        header = (
            f'"""Chapter {number}: {title}.\n\n'
            "Standalone construction code: no creditriskbook imports.\n"
            '"""\n\n'
        )
        path.write_text(header + EXAMPLES[number].rstrip() + "\n", encoding="utf-8")
        expected.add(path)
    for path in OUT.glob("chapter_*.py"):
        if path not in expected:
            path.unlink()
    print(f"Exported {len(expected)} standalone chapter scripts")


if __name__ == "__main__":
    main()
