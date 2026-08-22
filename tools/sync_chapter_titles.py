"""Synchronise chapter headings in the manuscript with ``book/structure.json``."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    structure = json.loads((ROOT / "book" / "structure.json").read_text(encoding="utf-8"))
    titles = {
        int(chapter["number"]): str(chapter["title"])
        for part in structure["parts"]
        for chapter in part["chapters"]
    }
    replaced: set[int] = set()
    pattern = re.compile(r"^# Chapter (\d+) — .+$", flags=re.MULTILINE)
    for path in sorted((ROOT / "book" / "full_manuscript").glob("*.md")):
        text = path.read_text(encoding="utf-8")

        def replacement(match: re.Match[str]) -> str:
            number = int(match.group(1))
            if number not in titles:
                raise KeyError(f"Chapter {number} is absent from book/structure.json")
            replaced.add(number)
            return f"# Chapter {number} — {titles[number]}"

        updated = pattern.sub(replacement, text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    missing = set(titles) - replaced
    if missing:
        raise RuntimeError(f"No manuscript heading found for chapters: {sorted(missing)}")
    print(f"Synchronised {len(replaced)} chapter titles")


if __name__ == "__main__":
    main()
