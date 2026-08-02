"""Validate the expanded manuscript before document generation."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "book" / "full_manuscript"
STRUCTURE = ROOT / "book" / "structure.json"
GUIDED_LABS = ROOT / "book" / "guided_labs"


def chapter_sections(text: str) -> list[tuple[int, str, str]]:
    headings = list(re.finditer(r"^# Chapter (\d+) — (.+)$", text, re.MULTILINE))
    sections = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections.append((int(match.group(1)), match.group(2).strip(), text[match.start() : end]))
    return sections


def main() -> None:
    structure = json.loads(STRUCTURE.read_text(encoding="utf-8"))
    expected = {
        chapter["number"]: chapter["title"]
        for part in structure["parts"]
        for chapter in part["chapters"]
    }
    files = sorted(MANUSCRIPT.glob("*.md"))
    assert files, "Expanded manuscript is missing"
    lab_files = sorted(GUIDED_LABS.glob("chapter_*.md"))
    assert len(lab_files) == 72, f"Expected 72 guided laboratories, found {len(lab_files)}"
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in [*files, *lab_files])
    chapter_text = "\n".join(
        path.read_text(encoding="utf-8") for path in files if "_part_" in path.name
    )
    chapters = chapter_sections(chapter_text)
    observed = {number: title for number, title, _ in chapters}

    assert len(chapters) == 72, f"Expected 72 chapters, found {len(chapters)}"
    assert list(observed) == list(range(1, 73)), "Chapters must be ordered 1 through 72"
    assert observed == expected, "Chapter headings differ from book/structure.json"

    for number, _, section in chapters:
        words = re.findall(r"\b[\w'-]+\b", section)
        assert len(words) >= 150, f"Chapter {number} has insufficient analytical content"
        assert "```" in section, f"Chapter {number} requires a code example"
        assert re.search(r"(?i)lab|exercise", section), f"Chapter {number} requires a lab"
        assert re.search(r"^## ", section, re.MULTILINE), f"Chapter {number} needs subsections"

    cases = re.findall(r"^### Case (\d+) — ", all_text, re.MULTILINE)
    assert [int(value) for value in cases] == list(range(1, 73)), "Casebook must cover 1–72"

    citations = {int(value) for value in re.findall(r"\[R(\d+)\]", all_text)}
    definitions = {int(value) for value in re.findall(r"^\[R(\d+)\] ", all_text, re.MULTILINE)}
    assert citations <= definitions, f"Undefined references: {sorted(citations - definitions)}"
    assert len(definitions) >= 35, "Reference ledger is not sufficiently broad"

    word_count = len(re.findall(r"\b[\w'-]+\b", all_text))
    assert word_count >= 90_000, f"Manuscript has only {word_count:,} words"
    assert all_text.count("```python") >= 140, "Expected extensive Python examples"
    assert all_text.count(r"\[") >= 80, "Expected extensive display mathematics"
    for index, block in enumerate(
        re.findall(r"```python\n(.*?)\n```", all_text, re.DOTALL), start=1
    ):
        compile(block, f"manuscript-python-block-{index}", "exec")
    print(
        f"Validated {len(chapters)} chapters, {len(cases)} cases, "
        f"{len(definitions)} references and {word_count:,} words."
    )


if __name__ == "__main__":
    main()
