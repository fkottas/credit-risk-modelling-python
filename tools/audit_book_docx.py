"""Audit native equations, internal navigation, and pagination controls in the book DOCX."""

from __future__ import annotations

import argparse
import re
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}


def _text(element: etree._Element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS)).strip()


def _enabled(nodes: list[etree._Element]) -> bool:
    return any(node.get(f"{{{W}}}val", "1") not in {"0", "false", "off"} for node in nodes)


def audit(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
        styles = etree.fromstring(archive.read("word/styles.xml"))

    bookmark_names = [
        node.get(f"{{{W}}}name") for node in root.xpath("//w:bookmarkStart", namespaces=NS)
    ]
    bookmark_counts = Counter(bookmark_names)
    assert bookmark_counts["book_contents"] == 1
    for number in range(1, 73):
        name = f"chapter_{number:03d}"
        assert bookmark_counts[name] == 1, f"Missing or duplicate chapter bookmark: {name}"
    assert not any(name and name.startswith("CRB_NAV") for name in bookmark_names)

    anchors = root.xpath("//w:hyperlink/@w:anchor", namespaces=NS)
    unresolved = sorted(set(anchors) - set(bookmark_names))
    assert not unresolved, f"Unresolved internal links: {unresolved}"
    for number in range(1, 73):
        anchor = f"chapter_{number:03d}"
        assert anchors.count(anchor) >= 3, f"Contents entry is not fully linked: {anchor}"

    # The first table is the static, linked contents table. Label, title, and
    # rendered page number must all resolve to the same bookmark.
    toc = root.xpath("//w:body/w:tbl[1]", namespaces=NS)[0]
    rows = toc.xpath("./w:tr", namespaces=NS)
    assert len(rows) >= 90, f"Contents table is unexpectedly short: {len(rows)} rows"
    for row_number, row in enumerate(rows, start=1):
        cells = row.xpath("./w:tc", namespaces=NS)
        assert len(cells) == 3
        cell_anchors = [cell.xpath(".//w:hyperlink/@w:anchor", namespaces=NS) for cell in cells]
        assert all(len(items) == 1 for items in cell_anchors), (
            f"Contents row {row_number} does not link label, title, and page"
        )
        assert len({items[0] for items in cell_anchors}) == 1
        assert re.fullmatch(r"\d+", _text(cells[2])), (
            f"Contents row {row_number} has no rendered page number"
        )

    math_objects = root.xpath("//m:oMath", namespaces=NS)
    assert len(math_objects) >= 250, f"Too few native Word equations: {len(math_objects)}"
    nary_characters = root.xpath("//m:naryPr/m:chr/@m:val", namespaces=NS)
    assert "∑" in nary_characters, "No native summation operator was found"
    assert "∏" in nary_characters, "No native product operator was found"
    assert "Σ" not in nary_characters, "Capital Sigma was incorrectly used as a summation"
    assert root.xpath("//m:f", namespaces=NS), "No native Word fractions were found"
    assert root.xpath("//m:rad", namespaces=NS), "No native Word radicals were found"
    math_text = " ".join(root.xpath("//m:t/text()", namespaces=NS))
    assert not re.search(r"\\(?:sum|prod|frac|sqrt|begin|end)\b", math_text), (
        "Visible LaTeX commands remain in Word equations"
    )

    normal = styles.xpath("//w:style[@w:styleId='Normal']/w:pPr", namespaces=NS)[0]
    assert not _enabled(normal.xpath("./w:keepLines", namespaces=NS)), (
        "Normal paragraphs are still forced to remain on one page"
    )
    heading_one = styles.xpath("//w:style[@w:styleId='Heading1']/w:pPr", namespaces=NS)[0]
    assert not _enabled(heading_one.xpath("./w:pageBreakBefore", namespaces=NS)), (
        "Every chapter is still forced onto a new page"
    )
    split_blockers = root.xpath(
        "//w:tr[w:trPr/w:cantSplit and not(w:trPr/w:tblHeader)]", namespaces=NS
    )
    assert not split_blockers, f"{len(split_blockers)} non-header table rows still block page flow"

    print(
        "DOCX audit passed: "
        f"{len(math_objects)} native equations, {len(set(anchors))} link targets, "
        f"{len(rows)} linked contents rows."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    arguments = parser.parse_args()
    audit(arguments.docx.resolve())


if __name__ == "__main__":
    main()
