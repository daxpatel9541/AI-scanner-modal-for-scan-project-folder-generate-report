from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    upload_type = models.CharField(max_length=50, default='zip')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Scan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scans')
    total_issues = models.IntegerField(default=0)
    total_files_scanned = models.IntegerField(default=0)
    risk_score = models.FloatField(default=0.0)
    risk_percentage = models.FloatField(default=0.0)
    security_grade = models.CharField(max_length=5, default='A')
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.id} for {self.project.name} - Grade {self.security_grade}"

class Vulnerability(models.Model):
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='vulnerabilities')
    file_name = models.CharField(max_length=500)
    line_number = models.IntegerField()
    vulnerability_type = models.TextField()
    severity = models.CharField(max_length=50)
    explanation = models.TextField()
    fix_suggestion = models.TextField()
    impact_analysis = models.TextField(null=True, blank=True)
    code_snippet = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.severity} - {self.vulnerability_type} in {self.file_name}"
