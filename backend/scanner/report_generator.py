import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

def generate_enterprise_report(scan, vulnerabilities, file_path):
    """
    Generates a professional enterprise-grade PDF security report.
    """
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor("#1e293b")
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor("#2563eb")
    )

    # 1. Cover Page / Header
    story.append(Paragraph(f"Security Audit: {scan.project.name}", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))

    # 2. Executive Summary
    story.append(Paragraph("Executive Summary", section_style))
    
    summary_data = [
        ["Metric", "Value"],
        ["Project Name", scan.project.name],
        ["Total Vulnerabilities", str(scan.total_issues)],
        ["Security Grade", scan.security_grade],
        ["Risk Percentage", f"{scan.risk_percentage:.1f}%"],
        ["Status", "Production Ready" if scan.security_grade in ['A', 'B'] else "Action Required"]
    ]
    
    t = Table(summary_data, colWidths=[2 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#475569")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * inch))

    # 3. Detailed Findings
    story.append(PageBreak())
    story.append(Paragraph("Detailed Findings", section_style))

    for vuln in vulnerabilities:
        story.append(Paragraph(f"{vuln.vulnerability_type}", styles['Heading3']))
        
        detail_data = [
            ["Severity", vuln.severity],
            ["File Path", vuln.file_name],
            ["Line Number", str(vuln.line_number)],
        ]
        
        dt = Table(detail_data, colWidths=[1.5 * inch, 4 * inch])
        dt.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc"))
        ]))
        story.append(dt)
        story.append(Spacer(1, 0.1 * inch))
        
        story.append(Paragraph("<b>Business Impact:</b>", styles['Normal']))
        story.append(Paragraph(vuln.impact_analysis or "High potential for unauthorized data access or system compromise.", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        story.append(Paragraph("<b>AI Security Explanation:</b>", styles['Normal']))
        story.append(Paragraph(vuln.explanation, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        story.append(Paragraph("<b>Secure Code Recommendation:</b>", styles['Normal']))
        code_style = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=9, leftIndent=20, leading=12)
        story.append(Paragraph(vuln.fix_suggestion.replace("\n", "<br/>"), code_style))
        
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("-" * 80, styles['Normal']))

    # 4. Final Recommendations
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Final Security Recommendations", section_style))
    recs = [
        "1. Implement strict input validation for all user-facing entry points.",
        "2. Enable automated security linting in your CI/CD pipeline.",
        "3. Conduct a manual peer review of all high-severity findings.",
        "4. Rotate all credentials found in the codebase (if any)."
    ]
    for rec in recs:
        story.append(Paragraph(rec, styles['Normal']))

    doc.build(story)
    return file_path
