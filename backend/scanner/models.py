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
    risk_score = models.FloatField(default=0.0)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.id} for {self.project.name}"

class Vulnerability(models.Model):
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='vulnerabilities')
    file_name = models.CharField(max_length=500)
    line_number = models.IntegerField()
    vulnerability_type = models.CharField(max_length=255)
    severity = models.CharField(max_length=50)
    explanation = models.TextField()
    fix_suggestion = models.TextField()

    def __str__(self):
        return f"{self.severity} - {self.vulnerability_type} in {self.file_name}"
