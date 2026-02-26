import os
import time
import tempfile
import zipfile
import shutil
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from .models import Project, Scan, Vulnerability
from .logic.scannerEngine import ScannerEngine
from .logic.severityEngine import SeverityEngine
from .logic.reportGenerator import ReportGenerator
from .serializers import ScanSerializer

import logging

logger = logging.getLogger(__name__)

class ScanUploadView(APIView):
    def post(self, request, format=None):
        try:
            mode = request.data.get('mode', 'file')
            project_name = request.data.get('projectName', 'Unnamed Project')
            
            # Enterprise Persistence
            user, _ = User.objects.get_or_create(username='demo_user')
            project, _ = Project.objects.get_or_create(user=user, name=project_name)

            # Use local temp directory to avoid Windows path length issues
            temp_base = os.path.join(settings.BASE_DIR, 'temp_scans')
            os.makedirs(temp_base, exist_ok=True)
            temp_project_dir = tempfile.mkdtemp(dir=temp_base)
            scan_target = ""

            # PHASE 1: Asset Reconstruction
            try:
                if mode == 'file':
                    file_obj = request.FILES.get('file')
                    if not file_obj:
                        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if file_obj.name.endswith('.zip'):
                        path = default_storage.save('temp/' + file_obj.name, file_obj)
                        scan_target = temp_project_dir
                        try:
                            with zipfile.ZipFile(default_storage.path(path), 'r') as zip_ref:
                                zip_ref.extractall(temp_project_dir)
                        finally:
                            default_storage.delete(path)
                    else:
                        path = default_storage.save('temp/' + file_obj.name, file_obj)
                        scan_target = default_storage.path(path)
                else:
                    files = request.FILES.getlist('files')
                    paths = request.data.getlist('paths')
                    if not paths: paths = request.POST.getlist('paths')

                    if not files:
                        return Response({"error": "No files found in upload. Check project permissions."}, status=status.HTTP_400_BAD_REQUEST)

                    logger.info(f"Reconstructing {len(files)} files for {project_name}")
                    for f, p in zip(files, paths):
                        p = os.path.normpath(p.lstrip('/\\').replace('../', ''))
                        target_path = os.path.join(temp_project_dir, p)
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with open(target_path, 'wb+') as destination:
                            for chunk in f.chunks():
                                destination.write(chunk)
                    scan_target = temp_project_dir
            except Exception as e:
                logger.error(f"PHASE 1 (Reconstruction) Failed: {e}")
                return Response({"error": f"Failed to reconstruct project: {str(e)}"}, status=500)

            # PHASE 2: Scanning Logic
            try:
                engine = ScannerEngine(scan_target)
                results = engine.scan()
                total_score, counts = SeverityEngine.calculate_risk_score(results)
                grade = SeverityEngine.calculate_grade(total_score)
                risk_percent = SeverityEngine.calculate_risk_percentage(total_score)
            except Exception as e:
                logger.error(f"PHASE 2 (Scanning) Failed: {e}")
                return Response({"error": f"Security Analysis Failed: {str(e)}"}, status=500)

            # PHASE 3: Data Persistence
            try:
                scan = Scan.objects.create(
                    project=project,
                    total_issues=len(results),
                    total_files_scanned=engine.total_files_scanned,
                    risk_score=total_score,
                    risk_percentage=risk_percent,
                    security_grade=grade,
                    status='completed'
                )

                for issue in results:
                    Vulnerability.objects.create(
                        scan=scan,
                        file_name=issue.get('file'),
                        line_number=issue.get('line', 0),
                        vulnerability_type=issue.get('vulnerabilityType'),
                        severity=issue.get('severity', 'LOW').upper(),
                        explanation=issue.get('description'),
                        impact_analysis=issue.get('description'),
                        fix_suggestion=issue.get('solution'),
                        code_snippet=issue.get('snippet', '')
                    )
            except Exception as e:
                logger.error(f"PHASE 3 (Persistence) Failed: {e}")
                return Response({"error": f"Failed to save scan results: {str(e)}"}, status=500)

            # PHASE 4: Report Generation
            try:
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reports'), exist_ok=True)
                report_name = f"report_{scan.id}.pdf"
                report_path = os.path.join(settings.MEDIA_ROOT, 'reports', report_name)
                
                reporter = ReportGenerator({
                    'total_files': engine.total_files_scanned,
                    'total_issues': len(results),
                    'risk_score': total_score,
                    'risk_percentage': risk_percent,
                    'security_grade': grade,
                    'issues': results,
                    'counts': counts
                }, project_name)
                
                reporter.generate_pdf(report_path)
                scan.report_file.name = f"reports/{report_name}"
                scan.save()
            except Exception as e:
                logger.warning(f"PHASE 4 (Reporting) Failed: {e}. Scan saved but PDF unavailable.")

            serializer = ScanSerializer(scan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Global Scan Failure")
            return Response({"error": f"Deep System Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Safer cleanup
            try:
                if temp_project_dir and os.path.exists(temp_project_dir):
                    shutil.rmtree(temp_project_dir)
            except Exception as ce:
                logger.warning(f"Cleanup failed: {ce}")

class ScanDownloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, scan_id):
        try:
            logger.info(f"Report download requested for Scan ID: {scan_id}")
            
            try:
                scan = Scan.objects.get(id=scan_id)
            except Scan.DoesNotExist:
                return Response({"error": "Scan record not found."}, status=404)

            # Prepare directories
            reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
            os.makedirs(reports_dir, exist_ok=True)

            # Strict PDF Enforcement: Regenerate if missing OR if it's a legacy JSON path
            current_path = scan.report_file.path if scan.report_file and scan.report_file.name else ""
            needs_regeneration = not current_path or not os.path.exists(current_path) or not current_path.lower().endswith('.pdf')

            if needs_regeneration:
                logger.info(f"Regenerating PDF for scan {scan.id} (needs_regen={needs_regeneration})")
                vulnerabilities = scan.vulnerabilities.all()
                results = []
                counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                for v in vulnerabilities:
                    results.append({
                        'file': v.file_name,
                        'line': v.line_number,
                        'vulnerabilityType': v.vulnerability_type,
                        'severity': v.severity,
                        'description': v.explanation,
                        'solution': v.fix_suggestion,
                        'snippet': v.code_snippet
                    })
                    counts[v.severity] = counts.get(v.severity, 0) + 1

                report_name = f"report_{scan.id}.pdf"
                file_path = os.path.join(reports_dir, report_name)
                
                reporter = ReportGenerator({
                    'total_files': scan.total_files_scanned,
                    'total_issues': len(results),
                    'risk_score': scan.risk_score,
                    'risk_percentage': scan.risk_percentage,
                    'security_grade': scan.security_grade,
                    'issues': results,
                    'counts': counts
                }, scan.project.name)
                reporter.generate_pdf(file_path)
                
                # Update DB with the correct PDF path
                scan.report_file.name = f"reports/{report_name}"
                scan.save()
            else:
                file_path = current_path

            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Security_Report_{scan.id}.pdf"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        except Exception as e:
            logger.exception(f"Report serving failed for {scan_id}")
            return Response({"error": f"Failed to generate/serve report: {str(e)}"}, status=500)

class ProjectHistoryView(APIView):
    def get(self, request):
        scans = Scan.objects.all().order_by('-created_at')
        serializer = ScanSerializer(scans, many=True)
        return Response(serializer.data)
