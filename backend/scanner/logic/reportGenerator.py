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
        Generates a standardized JSON report.
        """
        report = {
            "projectName": self.project_name,
            "scanDate": self.scan_date,
            "totalFilesScanned": self.data.get('total_files', 0),
            "totalIssuesFound": self.data.get('total_issues', 0),
            "criticalCount": self.data.get('counts', {}).get('CRITICAL', 0),
            "highCount": self.data.get('counts', {}).get('HIGH', 0),
            "mediumCount": self.data.get('counts', {}).get('MEDIUM', 0),
            "lowCount": self.data.get('counts', {}).get('LOW', 0),
            "riskScore": self.data.get('risk_score', 0),
            "riskPercentage": f"{self.data.get('risk_percentage', 0):.1f}%",
            "securityGrade": self.data.get('security_grade', 'F'),
            "issues": self.data.get('issues', [])
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        return file_path

    def _sanitize(self, text):
        """Clean string for PDF compatibility."""
        if not text: return ""
        # Remove non-printable characters and ensure valid unicode
        return "".join(c for c in str(text) if c.isprintable()).strip()

    def generate_pdf(self, file_path):
        """
        Generates a professional PDF report.
        """
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Styles
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20)
            header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=18, spaceBefore=15, spaceAfter=10, textColor=colors.blue)

            # Header
            story.append(Paragraph(self._sanitize(f"Security Audit Report: {self.project_name}"), title_style))
            story.append(Paragraph(f"Date: {self.scan_date}", styles['Normal']))
            story.append(Spacer(1, 0.5 * inch))

            # Executive Summary
            story.append(Paragraph("Executive Summary", header_style))
            summary_table = [
                ["Metric", "Value"],
                ["Security Grade", self.data.get('security_grade')],
                ["Risk Score", str(self.data.get('risk_score'))],
                ["Total Issues", str(self.data.get('total_issues'))],
                ["Files Scanned", str(self.data.get('total_files'))]
            ]
            t = Table(summary_table, colWidths=[2*inch, 3*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('PADDING', (0,0), (-1,-1), 6)
            ]))
            story.append(t)
            story.append(PageBreak())

            # Detailed Issues
            story.append(Paragraph("Detailed Findings", header_style))
            for issue in self.data.get('issues', []):
                v_type = self._sanitize(issue['vulnerabilityType'])
                story.append(Paragraph(f"<b>{v_type}</b> ({issue['severity']})", styles['Heading3']))
                
                loc = self._sanitize(f"Location: {issue['file']} (Line {issue['line']})")
                story.append(Paragraph(loc, styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
                
                desc = self._sanitize(issue['description'])
                story.append(Paragraph(f"Description: {desc}", styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
                
                sol = self._sanitize(issue['solution'])
                story.append(Paragraph(f"<b>Recommendation:</b> {sol}", styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph("-" * 80, styles['Normal']))

            doc.build(story)
            return file_path
        except Exception as e:
            print(f"PDF Build Error: {e}")
            raise e
