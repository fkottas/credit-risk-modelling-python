"""Build the review DOCX from Markdown.

Preset: compact_reference_guide. Header pattern: editorial_cover.
Named overrides: cover, part dividers, code blocks, reference text, wide tables.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "book" / "manuscript"
BLUE, DARK_BLUE, INK = "2E74B5", "1F4D78", "203748"
SUBTITLE, GOLD, MUTED = "2B5163", "8B6F28", "667788"
TABLE_FILL, LIGHT_FILL, CALLOUT_FILL = "E8EEF5", "F2F4F7", "F4F6F9"
PAGE_WIDTH_DXA = 9360


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    node = tc_pr.find(qn("w:shd"))
    if node is None:
        node = OxmlElement("w:shd")
        tc_pr.append(node)
    node.set(qn("w:fill"), fill)


def set_cell_width(cell, width: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    node = tc_pr.find(qn("w:tcW"))
    if node is None:
        node = OxmlElement("w:tcW")
        tc_pr.append(node)
    node.set(qn("w:w"), str(width))
    node.set(qn("w:type"), "dxa")


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    margins = tc_pr.find(qn("w:tcMar"))
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, *, color: str = "C8D4DF", size: int = 4) -> None:
    """Apply a restrained single grid that survives Word and PDF rendering."""
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_run_font(run, name="Calibri", size=None, color=None, bold=None, italic=None) -> None:
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def add_hyperlink(paragraph, text: str, url: str) -> None:
    relationship = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.extend([color, underline])
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.extend([r_pr, text_node])
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


INLINE = re.compile(r"(\*\*.*?\*\*|\*[^*]+\*|`.*?`|https?://[^\s)]+[\w/#])")


def add_inline(paragraph, text: str, *, size: float | None = None) -> None:
    position = 0
    for match in INLINE.finditer(text):
        if match.start() > position:
            set_run_font(paragraph.add_run(text[position : match.start()]), size=size)
        token = match.group(0)
        if token.startswith("**"):
            set_run_font(paragraph.add_run(token[2:-2]), size=size, bold=True)
        elif token.startswith("*"):
            set_run_font(paragraph.add_run(token[1:-1]), size=size, italic=True)
        elif token.startswith("`"):
            set_run_font(
                paragraph.add_run(token[1:-1]), name="Consolas", size=size or 9.5, color=DARK_BLUE
            )
        else:
            add_hyperlink(paragraph, token, token)
        position = match.end()
    if position < len(text):
        set_run_font(paragraph.add_run(text[position:]), size=size)


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", Pt(11)
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25
    normal.paragraph_format.widow_control = True
    normal.paragraph_format.keep_together = True
    tokens = {
        "Heading 1": (16, BLUE, 18, 10),
        "Heading 2": (13, BLUE, 14, 7),
        "Heading 3": (12, DARK_BLUE, 10, 5),
    }
    for name, (size, color, before, after) in tokens.items():
        style = doc.styles[name]
        style.font.name, style.font.size, style.font.bold = "Calibri", Pt(size), True
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before, style.paragraph_format.space_after = (
            Pt(before),
            Pt(after),
        )
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.keep_together = True
    doc.styles["Heading 1"].paragraph_format.page_break_before = True
    for name in ("Header", "Footer"):
        style = doc.styles[name]
        style.font.name, style.font.size = "Calibri", Pt(8.5)
        style.font.color.rgb = RGBColor.from_string(MUTED)
        style.paragraph_format.space_after = Pt(0)


def add_custom_numbering(doc: Document, *, bullet: bool) -> int:
    numbering = doc.part.numbering_part.element
    abs_ids = [int(n.get(qn("w:abstractNumId"))) for n in numbering.findall(qn("w:abstractNum"))]
    num_ids = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
    abstract_id, num_id = max(abs_ids, default=-1) + 1, max(num_ids, default=0) + 1
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(abstract_id))
    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "singleLevel")
    abstract.append(multi)
    level = OxmlElement("w:lvl")
    level.set(qn("w:ilvl"), "0")
    for tag, value in (
        ("start", "1"),
        ("numFmt", "bullet" if bullet else "decimal"),
        ("lvlText", "•" if bullet else "%1."),
        ("lvlJc", "left"),
    ):
        node = OxmlElement(f"w:{tag}")
        node.set(qn("w:val"), value)
        level.append(node)
    p_pr = OxmlElement("w:pPr")
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "num")
    tab.set(qn("w:pos"), "540")
    tabs.append(tab)
    indent = OxmlElement("w:ind")
    indent.set(qn("w:left"), "540")
    indent.set(qn("w:hanging"), "270")
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:after"), "80")
    spacing.set(qn("w:line"), "300")
    spacing.set(qn("w:lineRule"), "auto")
    p_pr.extend([tabs, indent, spacing])
    level.append(p_pr)
    abstract.append(level)
    numbering.append(abstract)
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(num_id))
    ref = OxmlElement("w:abstractNumId")
    ref.set(qn("w:val"), str(abstract_id))
    num.append(ref)
    numbering.append(num)
    return num_id


def apply_numbering(paragraph, num_id: int) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = OxmlElement("w:numPr")
    for tag, value in (("ilvl", "0"), ("numId", str(num_id))):
        node = OxmlElement(f"w:{tag}")
        node.set(qn("w:val"), value)
        num_pr.append(node)
    p_pr.append(num_pr)


def add_page_field(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_run_font(run, size=8.5, color=MUTED)
    for tag, value in (("fldChar", "begin"), ("instrText", " PAGE "), ("fldChar", "separate")):
        node = OxmlElement(f"w:{tag}")
        if tag == "fldChar":
            node.set(qn("w:fldCharType"), value)
        else:
            node.set(qn("xml:space"), "preserve")
            node.text = value
        run._r.append(node)
    text = OxmlElement("w:t")
    text.text = "1"
    run._r.append(text)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(end)


def configure_page(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.right_margin = section.bottom_margin = section.left_margin = (
        Inches(1)
    )
    section.header_distance = section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = True
    paragraph = section.header.paragraphs[0]
    run = paragraph.add_run("APPLIED CREDIT RISK WITH PYTHON  •  FIRST-EDITION REVIEW")
    set_run_font(run, size=8.5, color=MUTED, bold=True)
    add_page_field(section.footer.paragraphs[0])
    section.first_page_header.paragraphs[0].clear()
    section.first_page_footer.paragraphs[0].clear()


def add_cover(doc: Document) -> None:
    doc.add_paragraph().paragraph_format.space_after = Pt(78)
    kicker = doc.add_paragraph()
    kicker.alignment, kicker.paragraph_format.space_after = WD_ALIGN_PARAGRAPH.CENTER, Pt(18)
    set_run_font(kicker.add_run("APPLIED QUANTITATIVE FINANCE"), size=10.5, color=GOLD, bold=True)
    title = doc.add_paragraph()
    title.alignment, title.paragraph_format.space_after = WD_ALIGN_PARAGRAPH.CENTER, Pt(8)
    set_run_font(title.add_run("Applied Credit Risk with Python"), size=30, color=INK, bold=True)
    for text in ("Scorecards, IRB, IFRS 9, Deployment", "and Governed Agentic AI"):
        paragraph = doc.add_paragraph()
        paragraph.alignment, paragraph.paragraph_format.space_after = (
            WD_ALIGN_PARAGRAPH.CENTER,
            Pt(2),
        )
        set_run_font(paragraph.add_run(text), size=15, color=SUBTITLE)
    strapline = doc.add_paragraph()
    strapline.alignment = WD_ALIGN_PARAGRAPH.CENTER
    strapline.paragraph_format.space_before, strapline.paragraph_format.space_after = Pt(22), Pt(82)
    set_run_font(
        strapline.add_run("An application-first handbook with tested Python"),
        size=10.5,
        color=GOLD,
        italic=True,
    )
    author = doc.add_paragraph()
    author.alignment, author.paragraph_format.space_after = WD_ALIGN_PARAGRAPH.CENTER, Pt(4)
    set_run_font(author.add_run("Dr. Ferdinantos Kottas"), size=13, color=INK, bold=True)
    edition = doc.add_paragraph()
    edition.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(
        edition.add_run("First-edition review manuscript  •  August 2026"), size=10.5, color=MUTED
    )
    doc.add_page_break()


def add_toc(doc: Document) -> None:
    title = doc.add_paragraph("Contents", style="Heading 1")
    title.paragraph_format.page_break_before = False
    entries = [
        ("PART I", "The End-to-End Credit System"),
        ("Chapter 1", "Credit Risk as an Operating System"),
        ("Chapter 2", "Products, Borrowers and the Credit Lifecycle"),
        ("Chapter 3", "Basel IRB, IFRS 9, CECL and Responsible Lending"),
        ("Chapter 4", "Lawful Data, Architecture and Quality Engineering"),
        ("PART II", "PD, Scorecards and Machine Learning"),
        ("Chapter 5", "From-Scratch Binning, WOE and Characteristic Analysis"),
        ("Chapter 6", "Logistic Scorecards from Estimation to Reason Codes"),
        ("Chapter 7", "Machine-Learning Challengers and a Common Score Scale"),
        ("Chapter 8", "Evaluation, Calibration, Selection and Credit Economics"),
        ("Chapter 9", "Survival, Lifetime PD and Low-Default Portfolios"),
        ("PART III", "LGD, EAD, ECL and Capital"),
        ("Chapter 10", "Workout LGD, Cure and Recovery Modelling"),
        ("Chapter 11", "EAD, CCF and Revolving Exposure"),
        ("Chapter 12", "IFRS 9 and CECL Engines"),
        ("Chapter 13", "IRB Capital, Portfolio and Counterparty Risk"),
        ("Chapter 14", "Stress Testing and Decision Optimisation"),
        ("PART IV", "Production, Governance and Agentic AI"),
        ("Chapter 15", "Validation, UAT and Model Governance"),
        ("Chapter 16", "Deployment, Monitoring and Model Lifecycle"),
        ("Chapter 17", "Governed Agentic AI in Credit Risk"),
        ("Chapter 18", "Integrated Case Studies and Student Projects"),
        ("Appendices", "Repository, data, tests, formulas, model card and references"),
    ]
    table = doc.add_table(rows=len(entries), cols=2)
    table_geometry(table, [1650, 7710], indent_dxa=0)
    for row, (label, item) in zip(table.rows, entries, strict=False):
        is_part = label.startswith("PART")
        for index, (cell, value) in enumerate(zip(row.cells, (label, item), strict=False)):
            set_cell_width(cell, (1650, 7710)[index])
            set_cell_margins(cell, top=45, start=40, bottom=45, end=80)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            set_run_font(
                paragraph.add_run(value),
                size=9.5,
                color=GOLD if is_part else (DARK_BLUE if index == 0 else "1F2933"),
                bold=is_part or index == 0,
            )
        if is_part:
            set_cell_shading(row.cells[0], CALLOUT_FILL)
            set_cell_shading(row.cells[1], CALLOUT_FILL)
    doc.add_page_break()


def add_part_page(doc: Document, label: str, title: str) -> None:
    part = doc.add_paragraph()
    part.paragraph_format.page_break_before, part.paragraph_format.space_before = True, Pt(150)
    part.paragraph_format.space_after, part.alignment = Pt(18), WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(part.add_run(label.upper()), size=11, color=GOLD, bold=True)
    heading = doc.add_paragraph()
    heading.alignment, heading.paragraph_format.space_after = WD_ALIGN_PARAGRAPH.CENTER, Pt(10)
    set_run_font(heading.add_run(title), size=24, color=INK, bold=True)
    doc.add_page_break()


def table_geometry(table, widths: list[int], indent_dxa=120) -> None:
    table.alignment, table.autofit = WD_TABLE_ALIGNMENT.LEFT, False
    tbl_pr = table._tbl.tblPr
    width = tbl_pr.find(qn("w:tblW"))
    width.set(qn("w:w"), str(sum(widths)))
    width.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)
    indent = OxmlElement("w:tblInd")
    indent.set(qn("w:w"), str(indent_dxa))
    indent.set(qn("w:type"), "dxa")
    tbl_pr.append(indent)
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for item in widths:
        node = OxmlElement("w:gridCol")
        node.set(qn("w:w"), str(item))
        grid.append(node)


def add_code_block(doc: Document, code: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table_geometry(table, [PAGE_WIDTH_DXA])
    cell = table.cell(0, 0)
    set_cell_width(cell, PAGE_WIDTH_DXA)
    set_cell_margins(cell, 100, 140, 100, 140)
    set_cell_shading(cell, LIGHT_FILL)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after, paragraph.paragraph_format.line_spacing = Pt(0), 1.0
    set_run_font(paragraph.add_run(code.rstrip()), name="Consolas", size=8.5, color="243746")


def add_table(doc: Document, rows: list[list[str]]) -> None:
    columns = max(len(row) for row in rows)
    rows = [row + [""] * (columns - len(row)) for row in rows]
    if columns == 2:
        widths = [2700, 6660]
    else:
        widths = [PAGE_WIDTH_DXA // columns] * columns
        widths[-1] += PAGE_WIDTH_DXA - sum(widths)
    table = doc.add_table(rows=len(rows), cols=columns)
    set_table_borders(table)
    table_geometry(table, widths)
    for row_index, (word_row, values) in enumerate(zip(table.rows, rows, strict=False)):
        tr_pr = word_row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
        if row_index == 0:
            repeat = OxmlElement("w:tblHeader")
            repeat.set(qn("w:val"), "true")
            tr_pr.append(repeat)
        for column, (cell, value) in enumerate(zip(word_row.cells, values, strict=False)):
            set_cell_width(cell, widths[column])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index == 0:
                set_cell_shading(cell, TABLE_FILL)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after, paragraph.paragraph_format.line_spacing = (
                Pt(0),
                1.0,
            )
            add_inline(paragraph, value.strip(), size=9.0 if columns >= 4 else 9.5)
            if row_index == 0:
                for run in paragraph.runs:
                    run.bold = True


def add_callout(doc: Document, text: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table_geometry(table, [PAGE_WIDTH_DXA])
    cell = table.cell(0, 0)
    set_cell_width(cell, PAGE_WIDTH_DXA)
    set_cell_margins(cell, 100, 180, 100, 180)
    set_cell_shading(cell, CALLOUT_FILL)
    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
    add_inline(cell.paragraphs[0], text)


def markdown_blocks(text: str):
    lines, i, paragraph = text.splitlines(), 0, []

    def flush():
        nonlocal paragraph
        if paragraph:
            value = " ".join(item.strip() for item in paragraph).strip()
            paragraph = []
            return "paragraph", value
        return None

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            item = flush()
            if item:
                yield item
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            yield "code", "\n".join(code_lines)
        elif line.startswith("# "):
            item = flush()
            if item:
                yield item
            yield "h1", line[2:].strip()
        elif line.startswith("## "):
            item = flush()
            if item:
                yield item
            yield "h2", line[3:].strip()
        elif line.startswith("### "):
            item = flush()
            if item:
                yield item
            yield "h3", line[4:].strip()
        elif line.startswith("- "):
            item = flush()
            if item:
                yield item
            yield "bullet", line[2:].strip()
        elif re.match(r"^\d+\. ", line):
            item = flush()
            if item:
                yield item
            yield "number", re.sub(r"^\d+\. ", "", line).strip()
        elif line.startswith("> "):
            item = flush()
            if item:
                yield item
            yield "callout", line[2:].strip()
        elif (
            line.startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\|[\s:|-]+\|$", lines[i + 1])
        ):
            item = flush()
            if item:
                yield item
            rows = [[c.strip() for c in line.strip().strip("|").split("|")]]
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            yield "table", rows
            continue
        elif not line.strip():
            item = flush()
            if item:
                yield item
        else:
            paragraph.append(line)
        i += 1
    item = flush()
    if item:
        yield item


def add_manuscript(doc: Document, bullet_num: int, decimal_num: int) -> None:
    parts = {
        1: ("Part I", "The End-to-End Credit System"),
        5: ("Part II", "PD, Scorecards and Machine Learning"),
        10: ("Part III", "LGD, EAD, ECL and Capital"),
        15: ("Part IV", "Production, Governance and Agentic AI"),
    }
    previous_kind = None
    current_decimal_num = decimal_num
    for file_index, path in enumerate(sorted(MANUSCRIPT.glob("*.md"))):
        content = path.read_text(encoding="utf-8")
        if path.name == "00_front_matter.md":
            content = content[content.index("### About this book") :]
        chapter = int(re.match(r"(\d+)_", path.name).group(1))
        if chapter in parts:
            add_part_page(doc, *parts[chapter])
        for kind, value in markdown_blocks(content):
            if kind == "h1":
                paragraph = doc.add_paragraph(value, style="Heading 1")
                if file_index == 0:
                    paragraph.paragraph_format.page_break_before = False
            elif kind == "h2":
                doc.add_paragraph(value, style="Heading 2")
            elif kind == "h3":
                doc.add_paragraph(value, style="Heading 3")
            elif kind == "paragraph":
                paragraph = doc.add_paragraph()
                if value.startswith("[R"):
                    (
                        paragraph.paragraph_format.space_after,
                        paragraph.paragraph_format.line_spacing,
                    ) = Pt(5), 1.15
                    add_inline(paragraph, value, size=9.5)
                else:
                    add_inline(paragraph, value)
            elif kind in {"bullet", "number"}:
                if kind == "number" and previous_kind != "number":
                    current_decimal_num = add_custom_numbering(doc, bullet=False)
                paragraph = doc.add_paragraph()
                apply_numbering(paragraph, bullet_num if kind == "bullet" else current_decimal_num)
                add_inline(paragraph, value)
            elif kind == "code":
                add_code_block(doc, value)
            elif kind == "table":
                add_table(doc, value)
            elif kind == "callout":
                add_callout(doc, value)
            previous_kind = kind


def audit_document(doc: Document) -> None:
    section = doc.sections[0]
    assert section.page_width == Inches(8.5) and section.page_height == Inches(11)
    assert section.left_margin == Inches(1)
    assert doc.styles["Normal"].font.name == "Calibri" and doc.styles["Normal"].font.size == Pt(11)
    assert doc.styles["Heading 1"].font.size == Pt(16)
    assert len(doc.tables) >= 10
    headings = [p.text for p in doc.paragraphs if p.style.name == "Heading 1"]
    assert any(text.startswith("Chapter 18") for text in headings) and "Appendices" in headings


def build(output: Path) -> None:
    doc = Document()
    configure_styles(doc)
    configure_page(doc)
    bullet_num, decimal_num = (
        add_custom_numbering(doc, bullet=True),
        add_custom_numbering(doc, bullet=False),
    )
    doc.core_properties.title = "Applied Credit Risk with Python"
    doc.core_properties.subject = "Scorecards, IRB, IFRS 9, Deployment and Governed Agentic AI"
    doc.core_properties.author = "Dr. Ferdinantos Kottas"
    doc.core_properties.keywords = "credit risk, scorecard, IFRS 9, IRB, agentic AI, Python"
    add_cover(doc)
    add_toc(doc)
    add_manuscript(doc, bullet_num, decimal_num)
    update = doc.settings._element.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        doc.settings._element.append(update)
    update.set(qn("w:val"), "true")
    audit_document(doc)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "Applied_Credit_Risk_with_Python_First_Edition_Review.docx",
    )
    build(parser.parse_args().output.resolve())


if __name__ == "__main__":
    main()
