import requests
import os

def check_pdf_validity():
    base_url = "http://localhost:8000/api"
    resp = requests.get(f"{base_url}/history/")
    scans = resp.json()
    
    for scan in scans:
        scan_id = scan['id']
        print(f"\nChecking Scan ID: {scan_id}")
        pdf_resp = requests.get(f"{base_url}/download-report/{scan_id}/")
        
        if pdf_resp.status_code == 200:
            content = pdf_resp.content
            print(f"  Size: {len(content)} bytes")
            if content.startswith(b"%PDF-"):
                print("  Status: VALID PDF HEADER")
            else:
                print(f"  Status: INVALID PDF (Starts with: {content[:10]})")
        else:
            print(f"  Status: FAILED ({pdf_resp.status_code})")

if __name__ == "__main__":
    check_pdf_validity()
