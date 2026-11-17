"""
Disaster Resilience Situation Report (SITREP) Generator
Produces formal municipal-grade PDF reports (using ReportLab) and structured JSON/Markdown audits.
"""

import io
import time
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(simulation_result: Dict[str, Any], intervention_data: Dict[str, Any] = None) -> bytes:
    """Generates an executive PDF report and returns the raw bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        fontName='Helvetica-Bold'
    )
    
    sub_title_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        fontName='Helvetica'
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e293b"),
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    alert_style = ParagraphStyle(
        'AlertCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#b91c1c"),
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Header
    story.append(Paragraph("INFRASTRUCTURE RESILIENCE SITUATION REPORT (SITREP)", title_style))
    story.append(Paragraph("AI-Powered Urban Cascading Failure Assessment & Early Warning Directive", sub_title_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # Executive Summary Meta Table
    params = simulation_result.get("parameters", {})
    summary = simulation_result.get("final_summary", {})
    
    meta_data = [
        [
            Paragraph("<b>Target Region:</b> Mumbai BKC Coastal Basin", body_style),
            Paragraph(f"<b>Timestamp:</b> {time.strftime('%Y-%m-%d %H:%M:%S UTC')}", body_style)
        ],
        [
            Paragraph(f"<b>Rainfall Intensity:</b> {params.get('rainfall_mm_hr', 0)} mm/hr", body_style),
            Paragraph(f"<b>High Tide Level:</b> {params.get('high_tide_m', 0)} m Chart Datum", body_style)
        ],
        [
            Paragraph(f"<b>System Resilience Index:</b> {summary.get('final_resilience', 0)} / 100", body_style),
            Paragraph(f"<b>Total Citizens Impacted:</b> {summary.get('total_population_affected', 0):,}", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Critical Alerts
    story.append(Paragraph("1. Critical Infrastructure Vulnerability Audit", h2_style))
    
    failed_count = summary.get("total_failures", 0)
    degraded_count = summary.get("total_degraded", 0)
    hospitals = summary.get("critical_hospitals_affected", [])

    if failed_count > 0:
        alert_msg = f"CRITICAL HAZARD: {failed_count} core infrastructure nodes have suffered complete systemic failure, with {degraded_count} in degraded status."
        if hospitals:
            alert_msg += f" High-priority trauma facilities affected: {', '.join(hospitals)}."
        story.append(Paragraph(alert_msg, alert_style))
    else:
        story.append(Paragraph("Status Nominal: No infrastructure components have completely collapsed at this load level.", body_style))

    story.append(Spacer(1, 8))

    # Cascade Events Timeline Table
    story.append(Paragraph("2. Spatio-Temporal Cascade Propagation Sequence", h2_style))
    events = simulation_result.get("all_events", [])
    
    event_rows = [["Time", "Failure Vector", "Propagation Description"]]
    if not events:
        event_rows.append(["T+00m", "None", "All systems operating within acceptable safety margins."])
    else:
        for ev in events[:6]: # Show top events
            event_rows.append([
                f"T+{ev['time_min']:02d}m",
                ev.get("type", "CASCADE").replace("_", " "),
                ev.get("message", "")
            ])

    ev_table = Table(event_rows, colWidths=[55, 175, 290])
    ev_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(ev_table)
    story.append(Spacer(1, 12))

    # AI Countermeasure & Prevention Plan
    story.append(Paragraph("3. AI-Optimized Mitigation Directives", h2_style))
    
    if intervention_data and intervention_data.get("ai_top_recommendation"):
        top_rec = intervention_data["ai_top_recommendation"]
        rec_text = (
            f"<b>Primary Action:</b> {top_rec['title']}<br/>"
            f"<b>Expected Resilience Gain:</b> +{top_rec['resilience_delta_pct']}% | "
            f"<b>Failures Averted:</b> {top_rec['failures_prevented']} assets | "
            f"<b>Citizens Shielded:</b> {top_rec['population_protected']:,}<br/>"
            f"<b>Deployment Lead Time:</b> {top_rec['lead_time_min']} minutes | "
            f"<b>Resource Cost:</b> {top_rec['resource_cost']}"
        )
        story.append(Paragraph(rec_text, body_style))
    else:
        story.append(Paragraph("Activate high-capacity emergency dewatering pumps at BKC and enforce police green corridors along Western Express Highway to preserve critical hospital access.", body_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#94a3b8"), spaceAfter=8))
    story.append(Paragraph("This document was generated automatically by the Infrastructure Failure Chain Predictor (IFCP) AI Engine. Model: Heterogeneous Graph Convolutional Percolation (HGCP-v2). Authenticated for Municipal Emergency Response.", sub_title_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
