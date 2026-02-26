import requests
import os
import json

def test_full_flow():
    base_url = "http://localhost:8000/api"
    
    # 1. Trigger a fresh scan (mock upload)
    # We can't easily upload complex folders via script without zipping, 
    # but we can check the history and try to download the latest one.
    
    print("1. Fetching history...")
    resp = requests.get(f"{base_url}/history/")
    scans = resp.json()
    print(f"Scans found: {len(scans)}")
    
    if len(scans) > 0:
        last_scan = scans[0]
        scan_id = last_scan['id']
        print(f"2. Testing PDF download for Scan ID: {scan_id}")
        
        # We'll force regeneration by calling the endpoint (it regenerates if file missing)
        pdf_resp = requests.get(f"{base_url}/download-report/{scan_id}/")
        print(f"PDF download status: {pdf_resp.status_code}")
        print(f"Content-Type: {pdf_resp.headers.get('Content-Type')}")
        
        if pdf_resp.status_code == 200:
            content_len = len(pdf_resp.content)
            print(f"PDF Size: {content_len} bytes")
            if content_len > 1000:
                print("SUCCESS: PDF appears to be a valid non-empty file.")
            else:
                print("WARNING: PDF is very small. Might be empty or header-only.")
        else:
            print(f"FAILED: PDF download returned {pdf_resp.status_code}")
            print(pdf_resp.text)

if __name__ == "__main__":
    test_full_flow()
