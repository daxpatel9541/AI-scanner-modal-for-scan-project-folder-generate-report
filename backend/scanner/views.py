import os
import time
import tempfile
import zipfile
import shutil
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from .models import Project, Scan, Vulnerability
from .engine import aggregate_scan_results, calculate_enterprise_risk
from .report_generator import generate_enterprise_report
from .serializers import ScanSerializer

class ScanUploadView(APIView):
    def post(self, request, format=None):
        mode = request.data.get('mode', 'file')
        project_name = request.data.get('projectName', 'Unnamed Project')
        
        # Enterprise Persistence: Link scans to a demo user for safety
        user, _ = User.objects.get_or_create(username='demo_user')
        project, _ = Project.objects.get_or_create(user=user, name=project_name)

        temp_project_dir = tempfile.mkdtemp()
        scan_target = ""

        LOG_FILE = os.path.join(tempfile.gettempdir(), "scanner_failure_debug.log")
        def debug_log(msg):
            with open(LOG_FILE, "a") as f:
                f.write(f"[{time.ctime()}] {msg}\n")
        
        debug_log(f"--- New Scan Start (168 files check) ---")

        try:
            if mode == 'file':
                file_obj = request.FILES.get('file')
                if not file_obj:
                    debug_log("Error: No file uploaded")
                    return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
                
                path = default_storage.save('temp/' + file_obj.name, file_obj)
                scan_target = default_storage.path(path)
            else:
                files = request.FILES.getlist('files')
                paths = request.data.getlist('paths')
                
                debug_log(f"Folder mode: files={len(files)}, paths={len(paths)}")
                
                if not files:
                    debug_log("Error: No files in request.FILES")
                    return Response({"error": "No files uploaded for folder mode"}, status=status.HTTP_400_BAD_REQUEST)

                # Reconstruct directory structure
                for i, (f, p) in enumerate(zip(files, paths)):
                    # Sanitize path
                    p = p.lstrip('/').replace('../', '')
                    target_path = os.path.join(temp_project_dir, p)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    try:
                        with open(target_path, 'wb+') as destination:
                            for chunk in f.chunks():
                                destination.write(chunk)
                    except Exception as fe:
                        debug_log(f"File write error at {p}: {str(fe)}")
                
                scan_target = os.path.join(tempfile.gettempdir(), f"folder_scan_{int(time.time())}.zip")
                debug_log(f"Zipping to {scan_target}")
                with zipfile.ZipFile(scan_target, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, dirs_files in os.walk(temp_project_dir):
                        for file_name in dirs_files:
                            file_full_path = os.path.join(root, file_name)
                            zip_path = os.path.relpath(file_full_path, temp_project_dir)
                            zipf.write(file_full_path, zip_path)

            try:
                debug_log(f"Running engine on {scan_target}")
                results = aggregate_scan_results(scan_target)
                debug_log(f"Engine success: {len(results)} issues")
            except Exception as e:
                debug_log(f"Engine crash: {str(e)}")
                return Response({"error": f"Scanning engine error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Enterprise Risk Scoring
            total_score, risk_percent, grade = calculate_enterprise_risk(results)
            
            # Create Scan record
            scan = Scan.objects.create(
                project=project,
                total_issues=len(results),
                risk_score=total_score,
                risk_percentage=risk_percent,
                security_grade=grade,
                status='completed'
            )

            # Save vulnerabilities with impact analysis
            vulnerability_objects = []
            for issue in results:
                ai = issue.get('ai_analysis', {})
                vuln = Vulnerability.objects.create(
                    scan=scan,
                    file_name=issue.get('file'),
                    line_number=issue.get('line', 0),
                    vulnerability_type=issue.get('scanner') + ": " + issue.get('type'),
                    severity=issue.get('severity', 'LOW').upper(),
                    explanation=ai.get('impact', 'Potential security risk detected.'),
                    impact_analysis=ai.get('scenario', 'Attackers could exploit this to compromise the system.'),
                    fix_suggestion=ai.get('secure_code', '# Follow standard security practices.'),
                    code_snippet=issue.get('snippet', '')
                )
                vulnerability_objects.append(vuln)

            # 4. Generate Professional PDF Report
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reports'), exist_ok=True)
            report_name = f"report_{scan.id}_{int(time.time())}.pdf"
            report_path = os.path.join(settings.MEDIA_ROOT, 'reports', report_name)
            
            generate_enterprise_report(scan, vulnerability_objects, report_path)
            
            # Update scan with report file path
            scan.report_file.name = f"reports/{report_name}"
            scan.save()

            serializer = ScanSerializer(scan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            debug_log(f"Global View Error: {str(e)}\n{traceback.format_exc()}")
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if scan_target and os.path.exists(scan_target):
                # Only remove if it's the temp zip we created or we saved a zip
                if mode == 'folder' or scan_target.endswith('.zip'):
                    try: os.remove(scan_target)
                    except: pass
            if temp_project_dir and os.path.exists(temp_project_dir):
                shutil.rmtree(temp_project_dir)

class ScanDownloadView(APIView):
    """
    Dedicated view for secure report downloads.
    """
    def get(self, request, scan_id):
        try:
            scan = Scan.objects.get(id=scan_id)
            # In a real SaaS, we would validate: if scan.project.user != request.user: return 403
            
            if not scan.report_file:
                return Response({"error": "Report not generated yet."}, status=404)
                
            file_path = scan.report_file.path
            if os.path.exists(file_path):
                return FileResponse(
                    open(file_path, 'rb'), 
                    content_type='application/pdf',
                    as_attachment=True,
                    filename=os.path.basename(file_path)
                )
            else:
                raise Http404("Report file missing on server.")
        except Scan.DoesNotExist:
            raise Http404("Scan not found.")

class ProjectHistoryView(APIView):
    def get(self, request):
        # Disable persistent history as requested
        return Response([])
