from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Team_Meeting_Report_5.pdf"
NAVY = colors.HexColor("#172B66")
INK = colors.HexColor("#202020")
MUTED = colors.HexColor("#555555")


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#AEB6C4"))
    canvas.setLineWidth(0.6)
    canvas.line(0.75 * inch, 0.52 * inch, 7.75 * inch, 0.52 * inch)
    canvas.setFont("Times-Roman", 9)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.34 * inch, "ClearPolicy Team - Fall 2026")
    canvas.drawRightString(7.75 * inch, 0.34 * inch, f"Page {document.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.52 * inch,
        bottomMargin=0.72 * inch,
        title="Team Meeting Report 5: ClearPolicy Team",
        author="ClearPolicy Team",
    )
    title = ParagraphStyle(
        "ReportTitle", fontName="Times-Bold", fontSize=17, leading=21,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
    )
    subtitle = ParagraphStyle(
        "ReportSubtitle", fontName="Times-Roman", fontSize=11.5, leading=15,
        textColor=INK, alignment=TA_CENTER, spaceAfter=1,
    )
    section = ParagraphStyle(
        "SectionHeading", fontName="Times-Bold", fontSize=12.5, leading=16,
        textColor=NAVY, spaceBefore=10, spaceAfter=4, keepWithNext=True,
    )
    body = ParagraphStyle(
        "Body", fontName="Times-Roman", fontSize=11, leading=15,
        textColor=INK, spaceAfter=4,
    )
    item = ParagraphStyle(
        "ListItem", parent=body, leftIndent=18, firstLineIndent=-15,
        spaceAfter=3,
    )

    story = [
        Paragraph("TEAM MEETING REPORT 5: CLEARPOLICY TEAM", title),
        Paragraph("COMP 496: SENIOR DESIGN II", subtitle),
        Paragraph("FALL 2026", subtitle),
        Spacer(1, 7),
        HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#AEB6C4")),
        Spacer(1, 4),
        Paragraph("1 DETAILS", section),
        Paragraph("<b>Date:</b> October 20, 2026", body),
        Paragraph("<b>Members Present:</b> TJ, Amon, Anthony", body),
        Paragraph("2 AGENDA ITEMS", section),
        Paragraph("1. Review the app's approach to reading privacy-policy text.", item),
        Paragraph("2. Confirm the GPT model and API for the natural-language analysis.", item),
        Paragraph("3. Keep generated explanations separate from the rule-based Trust Score.", item),
        Paragraph("4. Review how the app supports its AI-generated takeaways with policy text.", item),
        Paragraph("3 ACCOMPLISHMENTS", section),
        Paragraph(
            "The team clarified that the app should use natural-language analysis rather than a fixed-label clause classifier. "
            "The current implementation uses GPT-6 Luna (<font name='Times-Bold'>gpt-6-luna</font>) through the OpenAI Responses API "
            "to generate a plain-language summary, quoted key points, wording to review, and reader questions. "
            "The backend checks that supporting excerpts appear in the submitted policy, and the structured response keeps these sections "
            "consistent for display without assigning fixed topic labels. "
            "The rules engine still calculates the Trust Score separately. Policy text is sent to OpenAI with response storage disabled "
            "(<font name='Times-Bold'>store=false</font>). The generated explanation is marked experimental because its accuracy has not "
            "yet been evaluated against a held-out benchmark.",
            body,
        ),
        Paragraph("4 DECISIONS", section),
        Paragraph("1. Use GPT-6 Luna (gpt-6-luna) through the OpenAI Responses API for the app's policy-text NLP.", item),
        Paragraph("2. Keep the AI explanation separate from rule findings and the Trust Score.", item),
        Paragraph("3. Present the explanation as experimental and include supporting policy quotations.", item),
        Paragraph("4. Before the next demo, configure the backend API key and review a live response using the sample policy.", item),
    ]
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
