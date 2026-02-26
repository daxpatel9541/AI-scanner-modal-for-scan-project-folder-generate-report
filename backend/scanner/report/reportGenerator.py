import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

class ReportGenerator:
    def __init__(self, scan_data, project_name):
        self.data = scan_data
        self.project_name = project_name
        self.scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate_json(self, file_path):
        """
        Generates a standardized JSON report for data analysis.
        """
        try:
            report = {
                "projectName": self._sanitize(self.project_name),
                "scanDate": self.scan_date,
                "summary": {
                    "totalFilesScanned": self.data.get('total_files', 0),
                    "totalIssuesFound": self.data.get('total_issues', 0),
                    "riskScore": self.data.get('risk_score', 0),
                    "riskPercentage": f"{self.data.get('risk_percentage', 0):.1f}%",
                    "securityGrade": self.data.get('security_grade', 'F'),
                    "severityCounts": self.data.get('counts', {})
                },
                "findings": self.data.get('issues', [])
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)
            return file_path
        except Exception as e:
            print(f"JSON Generation Error: {e}")
            raise e

    def _sanitize(self, text):
        """Clean string for PDF/JSON compatibility."""
        if not text: return ""
        # Remove non-printable characters and ensure valid unicode
        return "".join(c for c in str(text) if c.isprintable()).strip()

    def generate_pdf(self, file_path):
        """
        Generates a professional PDF security report.
        """
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
            styles = getSampleStyleSheet()
            story = []

            # Custom Styles
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.darkblue)
            header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=18, spaceBefore=15, spaceAfter=10, textColor=colors.blue)
            vuln_header_style = ParagraphStyle('VulnHeader', parent=styles['Heading3'], fontSize=14, spaceBefore=10, textColor=colors.red)
            normal_style = styles['Normal']
            code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=8, leftIndent=20, spaceBefore=5, spaceAfter=5, backColor=colors.lightgrey)

            # Header Section
            story.append(Paragraph(self._sanitize(f"Security Audit Report: {self.project_name}"), title_style))
            story.append(Paragraph(f"Analysis Date: {self.scan_date}", normal_style))
            story.append(Spacer(1, 0.4 * inch))

            # Executive Summary
            story.append(Paragraph("Executive Summary", header_style))
            summary_table = [
                ["Security Metric", "Status/Value"],
                ["Security Grade", self.data.get('security_grade')],
                ["Risk Score", f"{self.data.get('risk_score')} / 1000"],
                ["Total Issues detected", str(self.data.get('total_issues'))],
                ["Files Analyzed", str(self.data.get('total_files'))]
            ]
            
            # Color coding for security grade
            grade = self.data.get('security_grade', 'F')
            grade_color = colors.green if grade == 'A' else colors.orange if grade in ['B', 'C'] else colors.red

            t = Table(summary_table, colWidths=[2.5*inch, 3*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F0F4F8')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.darkblue),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (1,1), (1,1), grade_color),
                ('TEXTCOLOR', (1,1), (1,1), colors.white),
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.5 * inch))

            # Severity Breakdown
            story.append(Paragraph("Findings Breakdown", styles['Heading3']))
            counts = self.data.get('counts', {})
            breakdown_data = [["Severity", "Count"]]
            for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                breakdown_data.append([sev, str(counts.get(sev, 0))])
            
            bt = Table(breakdown_data, colWidths=[2*inch, 1*inch])
            bt.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ]))
            story.append(bt)
            story.append(PageBreak())

            # Detailed Findings
            story.append(Paragraph("Detailed Findings", header_style))
            issues = self.data.get('issues', [])
            if not issues:
                story.append(Paragraph("No critical security vulnerabilities were discovered during this scan.", normal_style))
            else:
                for idx, issue in enumerate(issues):
                    severity = issue.get('severity', 'LOW')
                    v_type = self._sanitize(issue['vulnerabilityType'])
                    
                    # Finding Label
                    story.append(Paragraph(f"Finding #{idx+1}: {v_type}", vuln_header_style))
                    
                    # Details Table
                    details = [
                        [f"Severity: {severity}", f"File: {issue['file']}"],
                        [f"Line: {issue['line']}", "Status: Open"]
                    ]
                    dt = Table(details, colWidths=[2.5*inch, 3*inch])
                    dt.setStyle(TableStyle([
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('TEXTCOLOR', (0,0), (0,0), colors.red if severity in ['CRITICAL', 'HIGH'] else colors.black),
                    ]))
                    story.append(dt)
                    story.append(Spacer(1, 0.1 * inch))

                    # Description & Recommendation
                    story.append(Paragraph(f"<b>Description:</b> {self._sanitize(issue['description'])}", normal_style))
                    story.append(Spacer(1, 0.05 * inch))
                    story.append(Paragraph(f"<b>Recommendation:</b> {self._sanitize(issue['solution'])}", normal_style))
                    
                    # Code Snippet
                    if issue.get('snippet'):
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(Paragraph("<b>Code Snippet:</b>", styles['Normal']))
                        story.append(Paragraph(self._sanitize(issue['snippet']).replace('\n', '<br/>'), code_style))
                    
                    story.append(Spacer(1, 0.2 * inch))
                    story.append(Paragraph("-" * 100, styles['Normal']))
                    story.append(Spacer(1, 0.2 * inch))

            doc.build(story)
            return file_path
        except Exception as e:
            print(f"PDF Build Error: {e}")
            raise e
