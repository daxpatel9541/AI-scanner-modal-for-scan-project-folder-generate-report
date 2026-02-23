import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from .models import Project, Scan, Vulnerability
from .engine import aggregate_scan_results
from .serializers import ScanSerializer

class ScanUploadView(APIView):
    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        project_name = request.data.get('projectName', 'Unnamed Project')
        
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure a default user exists for this demo
        user, _ = User.objects.get_or_create(username='demo_user')

        # Create Project
        project = Project.objects.create(user=user, name=project_name)

        # Save temporary file
        path = default_storage.save('temp/' + file_obj.name, file_obj)
        full_path = default_storage.path(path)

        try:
            # Run multi-scanner aggregation
            results = aggregate_scan_results(full_path)
            
            # Create Scan record
            scan = Scan.objects.create(
                project=project,
                total_issues=len(results),
                risk_score=self.calculate_risk_score(results),
                status='completed'
            )

            # Save vulnerabilities with AI explanations
            for issue in results:
                Vulnerability.objects.create(
                    scan=scan,
                    file_name=issue.get('file'),
                    line_number=issue.get('line', 0),
                    vulnerability_type=issue.get('scanner') + ": " + issue.get('type'),
                    severity=issue.get('severity', 'LOW').upper(),
                    explanation=issue.get('ai_explanation'),
                    fix_suggestion="AI Recommendation: Follow the best practices outlined in the explanation to secure your code."
                )

            serializer = ScanSerializer(scan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        finally:
            # Clean up temp file
            if os.path.exists(full_path):
                os.remove(full_path)

    def calculate_risk_score(self, issues):
        if not issues:
            return 0.0
        
        # Weighted scoring logic: Critical/High = 10, Medium = 4, Low = 1
        score = 0
        for issue in issues:
            sev = issue.get('severity', 'LOW').upper()
            if sev in ['HIGH', 'CRITICAL', 'ERROR']: score += 10
            elif sev in ['MEDIUM', 'WARNING']: score += 4
            else: score += 1
            
        # Normalize to 0-100 base
        return min(100, score)

class ProjectHistoryView(APIView):
    def get(self, request):
        scans = Scan.objects.all().order_by('-created_at')
        serializer = ScanSerializer(scans, many=True)
        return Response(serializer.data)
