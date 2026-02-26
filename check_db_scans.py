import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from scanner.models import Scan

def check_scans():
    scans = Scan.objects.all().order_by('-id')[:5]
    print(f"Checking last {len(scans)} scans:")
    for s in scans:
        print(f"Scan ID: {s.id}")
        print(f"  Project: {s.project.name}")
        print(f"  Total Issues: {s.total_issues}")
        print(f"  Total Files Scanned: {s.total_files_scanned}")
        print(f"  Report File: {s.report_file.name if s.report_file else 'None'}")
        if s.report_file:
            try:
                path = s.report_file.path
                if os.path.exists(path):
                    print(f"  File Size: {os.path.getsize(path)} bytes")
                else:
                    print(f"  File Missing on disk: {path}")
            except Exception as e:
                print(f"  Error checking path: {e}")
        print("-" * 20)

if __name__ == "__main__":
    check_scans()
