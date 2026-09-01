"""
PDF Export Engine for Vital Stats Suite
Generates:
1. Detailed Demographic Report (Complete breakdown of all 22 measures, tables, formulas, benchmarks)
2. Executive Summary Brief (Top 3-4 key concerns and plain-language policy findings)

Uses ReportLab with custom styling matching the editorial palette.
"""

from __future__ import annotations
import io
import os
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from engine.pipeline import DemographicPipelineResult


# Palette Colors for ReportLab
CLR_BG = colors.HexColor("#F5F1EA")
CLR_TEXT = colors.HexColor("#1F1B16")
CLR_TEXT_MUTED = colors.HexColor("#6B655C")
CLR_TERRACOTTA = colors.HexColor("#CC785C")
CLR_BORDER = colors.HexColor("#E5DFD3")
CLR_WHITE = colors.HexColor("#FFFFFF")
CLR_CRITICAL = colors.HexColor("#C05621")
CLR_SUCCESS = colors.HexColor("#2A9D8F")


def generate_detailed_pdf_report(
    result: DemographicPipelineResult,
    output_path: Optional[str] = None,
) -> bytes:
    """Generates a multi-page comprehensive demographic statistical PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer if output_path is None else output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=CLR_TEXT,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=CLR_TERRACOTTA,
        spaceAfter=14,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=CLR_TEXT,
        spaceBefore=14,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=CLR_TEXT,
    )
    muted_style = ParagraphStyle(
        "Muted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=CLR_TEXT_MUTED,
    )
    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=CLR_WHITE,
        alignment=TA_CENTER,
    )
    
    story = []
    
    # Title & Metadata
    story.append(Paragraph(f"Vital Statistics Suite — Demographic Report", title_style))
    meta_str = f"Dataset: <b>{result.dataset_name}</b>"
    if result.year:
        meta_str += f" | Year: <b>{result.year}</b>"
    if result.region:
        meta_str += f" | Region: <b>{result.region}</b>"
    meta_str += f" | Evaluated Measures: <b>{result.computable_count} / {result.total_measures_target}</b>"
    story.append(Paragraph(meta_str, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=CLR_TERRACOTTA, spaceAfter=12))
    
    # Executive Synthesis
    story.append(Paragraph("1. Executive Summary & Diagnostic Synthesis", section_heading))
    story.append(Paragraph(result.executive_summary, body_style))
    story.append(Spacer(1, 10))
    
    # Top Concerns Callout Table
    if result.top_concerns:
        concern_rows = [
            [
                Paragraph("<b>Priority Concern</b>", ParagraphStyle("Hdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
                Paragraph("<b>Severity</b>", ParagraphStyle("Hdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
                Paragraph("<b>Interpretation & Suggested Action</b>", ParagraphStyle("Hdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            ]
        ]
        for c in result.top_concerns:
            sev_bg = CLR_CRITICAL if c.get("severity") in ("CRITICAL", "SEVERE") else CLR_TERRACOTTA
            concern_rows.append([
                Paragraph(f"<b>{c.get('title', '')}</b>", body_style),
                Paragraph(f"<b>{c.get('severity', '')}</b>", ParagraphStyle("CSev", parent=body_style, textColor=sev_bg, fontName="Helvetica-Bold")),
                Paragraph(f"{c.get('description', '')} {c.get('recommendation', '')}", muted_style),
            ])
            
        t_concerns = Table(concern_rows, colWidths=[2.2 * inch, 1.0 * inch, 4.3 * inch])
        t_concerns.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), CLR_TEXT),
            ("TEXTCOLOR", (0, 0), (-1, 0), CLR_WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CLR_WHITE, colors.HexColor("#FAF7F2")]),
            ("GRID", (0, 0), (-1, -1), 0.5, CLR_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_concerns)
        story.append(Spacer(1, 14))
        
    # Data Quality Section
    story.append(Paragraph("2. Data Quality & Coverage Diagnostics", section_heading))
    q_rows = [
        [
            Paragraph("<b>Diagnostic Test</b>", ParagraphStyle("QHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Score / Index</b>", ParagraphStyle("QHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Status</b>", ParagraphStyle("QHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Evaluation & Recommendation</b>", ParagraphStyle("QHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
        ]
    ]
    for q_code, q in result.quality_checks.items():
        score_str = f"{q.score:.2f}" if q.score is not None else "N/A"
        q_rows.append([
            Paragraph(f"<b>{q.name}</b>", body_style),
            Paragraph(score_str, body_style),
            Paragraph(f"<b>{q.status}</b>", body_style),
            Paragraph(f"{q.interpretation}<br/><font color='#6B655C'><i>{q.recommendation}</i></font>", muted_style),
        ])
        
    t_qual = Table(q_rows, colWidths=[2.2 * inch, 0.9 * inch, 1.0 * inch, 3.4 * inch])
    t_qual.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CLR_TERRACOTTA),
        ("GRID", (0, 0), (-1, -1), 0.5, CLR_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CLR_WHITE, colors.HexColor("#FAF7F2")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_qual)
    story.append(Spacer(1, 14))
    
    # Detailed 22 Measures by Block
    story.append(Paragraph("3. Full Battery of Demographic Measures", section_heading))
    
    blocks = [
        ("A: Sex Composition", ["MP", "SR", "EXCESS_M"]),
        ("B: Age Composition & Dependency", ["ACR", "TDR", "CDR_CHILD", "OADR"]),
        ("C: Fertility", ["CBR", "MBR", "GFR", "ASFR", "TFR", "GRR", "NRR"]),
        ("D: Mortality & Standardization", ["CDR", "CORRECTED_CDR", "NMR", "IMR", "CMR", "ASDR", "DSDR", "SMR", "ISDR"]),
    ]
    
    m_rows = [
        [
            Paragraph("<b>Code</b>", ParagraphStyle("MHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Measure Name</b>", ParagraphStyle("MHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Value</b>", ParagraphStyle("MHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Status / Benchmark</b>", ParagraphStyle("MHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
            Paragraph("<b>Formula & Citation</b>", ParagraphStyle("MHdr", parent=body_style, textColor=CLR_WHITE, fontName="Helvetica-Bold")),
        ]
    ]
    
    for block_name, codes in blocks:
        # Block sub-header row
        m_rows.append([
            Paragraph(f"<b>{block_name}</b>", ParagraphStyle("BSub", parent=body_style, fontName="Helvetica-Bold", textColor=CLR_TERRACOTTA)),
            "", "", "", ""
        ])
        for code in codes:
            m = result.measures.get(code)
            if m:
                interp = m.interpretation or {}
                st_label = interp.get("label", "Standard")
                st_status = interp.get("status", "MODERATE")
                
                m_rows.append([
                    Paragraph(f"<b>{m.code}</b>", body_style),
                    Paragraph(m.name, body_style),
                    Paragraph(f"<b>{m.formatted_value}</b>", body_style),
                    Paragraph(f"<b>{st_status}</b>: {st_label}", muted_style),
                    Paragraph(f"<font size=7 color='#6B655C'>{m.formula}<br/><i>{m.citation}</i></font>", muted_style),
                ])
            else:
                m_rows.append([
                    Paragraph(f"<b>{code}</b>", muted_style),
                    Paragraph(code, muted_style),
                    Paragraph("<i>Not Computed</i>", muted_style),
                    Paragraph("Data gap", muted_style),
                    Paragraph("-", muted_style),
                ])
                
    t_meas = Table(m_rows, colWidths=[0.8 * inch, 1.8 * inch, 1.6 * inch, 1.8 * inch, 1.5 * inch])
    t_meas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CLR_TEXT),
        ("GRID", (0, 0), (-1, -1), 0.5, CLR_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CLR_WHITE, colors.HexColor("#FAF7F2")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meas)
    
    doc.build(story)
    
    if output_path is None:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    return b""


def generate_summary_pdf_brief(
    result: DemographicPipelineResult,
    output_path: Optional[str] = None,
) -> bytes:
    """Generates a concise 1-page plain-language executive briefing PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer if output_path is None else output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SummaryTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=CLR_TEXT,
    )
    sub_style = ParagraphStyle(
        "SummarySub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        textColor=CLR_TERRACOTTA,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=CLR_TEXT,
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14.5,
        textColor=CLR_TEXT,
    )
    
    story = []
    story.append(Paragraph(f"Executive Briefing: Demographic Assessment", title_style))
    story.append(Paragraph(f"Dataset: <b>{result.dataset_name}</b> | Year: {result.year or 'Current'} | Vital Stats Suite", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=CLR_TERRACOTTA, spaceAfter=12))
    
    story.append(Paragraph("Key Findings Summary", heading_style))
    story.append(Paragraph(result.executive_summary, body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Top Priority Demographic Findings & Action Items", heading_style))
    for i, c in enumerate(result.top_concerns, 1):
        sev_color = "#C05621" if c.get("severity") in ("CRITICAL", "SEVERE") else "#CC785C"
        story.append(Paragraph(
            f"<b>{i}. {c.get('title')}</b> <font color='{sev_color}'>[{c.get('severity')}]</font>",
            body_style
        ))
        story.append(Paragraph(f"{c.get('description')}", body_style))
        if c.get("recommendation"):
            story.append(Paragraph(f"<i>Recommendation: {c.get('recommendation')}</i>", ParagraphStyle("Rec", parent=body_style, textColor=CLR_TEXT_MUTED)))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    
    if output_path is None:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    return b""
