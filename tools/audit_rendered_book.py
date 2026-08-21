"""Inspect every rendered book page for blank pages and excessive bottom gaps."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def body_blank_fraction(path: Path) -> tuple[float, bool]:
    image = Image.open(path).convert("L")
    width, height = image.size
    # Exclude page furniture while retaining the full manuscript body region.
    body = image.crop(
        (int(0.08 * width), int(0.08 * height), int(0.92 * width), int(0.90 * height))
    )
    ink = body.point(lambda value: 255 if value < 238 else 0)
    bounds = ink.getbbox()
    if bounds is None:
        return 1.0, True
    last_ink = bounds[3] - 1
    return (body.height - 1 - last_ink) / body.height, False


def audit(directory: Path) -> None:
    pages = sorted(directory.glob("page-*.png"), key=lambda path: int(path.stem.split("-")[-1]))
    assert len(pages) >= 200, f"Expected a full book render, found {len(pages)} pages"
    measurements = []
    blank_pages = []
    for page in pages:
        fraction, blank = body_blank_fraction(page)
        page_number = int(page.stem.split("-")[-1])
        measurements.append((page_number, fraction))
        if blank:
            blank_pages.append(page_number)
    assert not blank_pages, f"Completely blank rendered pages: {blank_pages}"

    # The final page may be short. Elsewhere a half-empty page normally means a
    # forced chapter/part break, an unsplittable table row, or keep-together abuse.
    severe = [(number, fraction) for number, fraction in measurements[:-1] if fraction > 0.50]
    assert not severe, "Excessive body gaps remain before the final page: " + ", ".join(
        f"p.{number}={fraction:.0%}" for number, fraction in severe
    )
    moderate = [(number, fraction) for number, fraction in measurements if fraction > 0.35]
    assert len(moderate) <= 3, "Too many sparsely filled pages: " + ", ".join(
        f"p.{number}={fraction:.0%}" for number, fraction in moderate
    )
    print(
        f"Rendered-page audit passed: {len(pages)} pages, no blanks, "
        f"{len(moderate)} pages with more than 35% unused body depth."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("render_directory", type=Path)
    arguments = parser.parse_args()
    audit(arguments.render_directory.resolve())


if __name__ == "__main__":
    main()
