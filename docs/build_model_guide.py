from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Privacy_Policy_Analyzer_AI_Model_Guide.docx"
TEAL = "176B57"
INK = "22313A"
MUTED = "5F6D74"
PALE = "EAF3EF"
SAND = "F7F3E9"
LINE = "D8E2DE"


def set_cell_shading(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def add_hyperlink(paragraph, text: str, url: str) -> None:
    part = paragraph.part
    relationship_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), TEAL)
    properties.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    properties.append(underline)
    run.append(properties)
    value = OxmlElement("w:t")
    value.text = text
    run.append(value)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def set_repeat_table_header(row) -> None:
    properties = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    properties.append(repeat)


def set_run_font(run, size=None, bold=None, color=INK, italic=None):
    run.font.name = "Arial"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Arial")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Arial")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    return run


def add_body(doc, text, *, color=INK, size=10.5, after=5, bold_lead=None):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.12
    if bold_lead and text.startswith(bold_lead):
        set_run_font(paragraph.add_run(bold_lead), size=size, bold=True, color=color)
        set_run_font(paragraph.add_run(text[len(bold_lead):]), size=size, color=color)
    else:
        set_run_font(paragraph.add_run(text), size=size, color=color)
    return paragraph


def add_bullet(doc, text):
    paragraph = doc.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.left_indent = Inches(0.22)
    paragraph.paragraph_format.first_line_indent = Inches(-0.12)
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.line_spacing = 1.08
    set_run_font(paragraph.add_run(text), size=10.1, color=INK)
    return paragraph


def add_heading(doc, text, level=1):
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.space_before = Pt(8 if level == 1 else 5)
    paragraph.paragraph_format.space_after = Pt(4)
    set_run_font(paragraph.add_run(text), size=16 if level == 1 else 11.5, bold=True, color=INK)
    return paragraph


def add_table(doc, headers, rows, widths=None, font_size=9.2):
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    table.style = "Table Grid"
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "D9D9D9")
        borders.append(border)
    table._tbl.tblPr.append(borders)
    set_repeat_table_header(table.rows[0])
    for index, label in enumerate(headers):
        cell = table.rows[0].cells[index]
        if widths:
            cell.width = Inches(widths[index])
        set_cell_shading(cell, TEAL)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        set_run_font(paragraph.add_run(label), size=font_size, bold=True, color="FFFFFF")
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            if widths:
                cells[index].width = Inches(widths[index])
            set_cell_margins(cells[index])
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index % 2 == 1:
                set_cell_shading(cells[index], "F5F8F6")
            paragraph = cells[index].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.05
            set_run_font(paragraph.add_run(str(value)), size=font_size, color=INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_callout(doc, title: str, body: str, fill=PALE):
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Inches(6.95)
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    set_cell_margins(cell, top=150, start=190, bottom=150, end=190)
    first = cell.paragraphs[0]
    first.paragraph_format.space_after = Pt(3)
    set_run_font(first.add_run(title), size=10.5, bold=True, color=TEAL)
    second = cell.add_paragraph()
    second.paragraph_format.space_after = Pt(0)
    second.paragraph_format.line_spacing = 1.08
    set_run_font(second.add_run(body), size=9.7, color=INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(0.62)
    section.bottom_margin = Inches(0.62)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    styles = doc.styles
    styles["Title"].font.name = "Arial"
    styles["Title"]._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    styles["Title"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    styles["Title"].font.color.rgb = RGBColor.from_string("000000")
    styles["Title"].font.size = Pt(27)
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    for name in ("Heading 1", "Heading 2"):
        styles[name].font.name = "Arial"
        styles[name]._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        styles[name]._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run_font(header.add_run("COMP 496  /  PRIVACY POLICY ANALYZER"), size=8, bold=True, color=MUTED)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(footer.add_run("AI MODEL TECHNICAL GUIDE  |  October 2026  |  Page "), size=8, color=MUTED)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def build() -> None:
    doc = Document()
    configure_document(doc)

    eyebrow = doc.add_paragraph()
    eyebrow.paragraph_format.space_before = Pt(11)
    eyebrow.paragraph_format.space_after = Pt(8)
    set_run_font(eyebrow.add_run("CURRENT RUNTIME MODEL  /  NOVEMBER 2026"), size=9, bold=True, color=TEAL)
    title = doc.add_paragraph(style="Title")
    title.paragraph_format.space_after = Pt(5)
    title.paragraph_format.keep_with_next = True
    set_run_font(title.add_run("ClearPolicy Natural Language Summary"), size=27, bold=True, color="000000")
    add_body(doc, "ClearPolicy uses GPT to turn submitted privacy-policy text into a readable overview with source quotations, review points, and questions. The app presents the generated explanation as its analysis; it does not make a legal determination.", color=MUTED, size=11, after=10)

    add_heading(doc, "Model at a glance")
    add_table(
        doc,
        ["Setting", "Current value"],
        [
            ["Model", "GPT-6 Luna (gpt-6-luna), configurable with OPENAI_MODEL"],
            ["API", "OpenAI Responses API"],
            ["Task", "Generate a reader-focused explanation of the full policy text"],
            ["Training", "The project does not fine-tune the hosted model"],
            ["Response storage", "The request sets store=false"],
        ],
        widths=[1.55, 5.55],
        font_size=9.2,
    )

    add_heading(doc, "What the model returns")
    add_body(doc, "The backend sends the complete policy text to GPT-6 Luna. The model writes a short overview in everyday language, highlights useful details with quotations, identifies specific wording a reader may want to review, and suggests practical questions.")
    add_body(doc, "Structured Outputs keeps the response organized into the fields the interface displays. The interface presents one explanation that readers can trace back to the source text.")

    add_heading(doc, "How an analysis works")
    add_table(
        doc,
        ["Stage", "Action"],
        [
            ["1. React interface", "Sends the pasted policy text to the Flask backend."],
            ["2. Flask API", "Validates the text size and calls the configured GPT model."],
            ["3. OpenAI Responses API", "Returns the structured explanation; response storage is disabled with store=false."],
            ["4. Quote check", "The backend removes highlighted excerpts that do not appear in the submitted text."],
            ["5. Results screen", "Displays the overview, key details, review wording, and reader questions."],
        ],
        widths=[1.65, 5.45],
        font_size=9.0,
    )

    add_heading(doc, "Grounding and limitations")
    add_body(doc, "The prompt asks the model to explain only what the submitted text supports and to avoid legal, fairness, or trustworthiness judgments. Key details and review points include short quotations. The backend checks that each quotation occurs in the policy text, but an exact quote does not guarantee that its explanation is complete or correct.")
    add_body(doc, "The response contains summary, key_points, things_to_review, and reader_questions. The project has not yet evaluated summary quality against a held-out set of policies reviewed by people. Users should compare important statements with the complete policy.")

    add_heading(doc, "Privacy and configuration")
    add_body(doc, "Policy text is sent to OpenAI for analysis. The app sets store=false on the Responses API request. The project backend does not save submitted text to a database or application logs. Review the API account's data controls before using this prototype with sensitive material.")
    add_body(doc, "Set OPENAI_API_KEY in the backend environment before starting Flask; do not place the key in the React frontend. The model ID defaults to gpt-6-luna and can be changed with OPENAI_MODEL. The /healthz endpoint reports the configured model ID.")

    add_heading(doc, "Intended use")
    add_body(doc, "The generated explanation is an educational reading aid. It may omit details, misinterpret wording, or miss context in an incomplete document. It does not establish what an organization does in practice and is not legal advice or a legal compliance determination.")

    add_heading(doc, "OpenAI API references")
    sources = doc.add_paragraph()
    sources.paragraph_format.space_before = Pt(2)
    sources.paragraph_format.space_after = Pt(3)
    set_run_font(sources.add_run("Model catalog: "), size=9.1, bold=True, color=INK)
    add_hyperlink(sources, "OpenAI models", "https://developers.openai.com/api/docs/models")
    set_run_font(sources.add_run("  |  API: "), size=9.1, color=INK)
    add_hyperlink(sources, "Responses API", "https://developers.openai.com/api/reference/resources/responses/methods/create")
    set_run_font(sources.add_run("  |  Output format: "), size=9.1, color=INK)
    add_hyperlink(sources, "Structured Outputs", "https://developers.openai.com/api/docs/guides/structured-outputs")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)

if __name__ == "__main__":
    build()