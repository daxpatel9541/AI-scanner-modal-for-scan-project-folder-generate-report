import requests
import os
import time

def test_flow():
    base_url = "http://localhost:8000/api"
    
    print("1. Checking history...")
    resp = requests.get(f"{base_url}/history/")
    print(f"History status: {resp.status_code}")
    print(f"Scans found: {len(resp.json())}")
    
    if len(resp.json()) > 0:
        last_scan = resp.json()[0]
        scan_id = last_scan['id']
        print(f"2. Attempting download for Scan ID: {scan_id}")
        
        # Test PDF
        pdf_resp = requests.get(f"{base_url}/download-report/{scan_id}/?format=pdf")
        print(f"PDF download status: {pdf_resp.status_code}")
        print(f"Content-Type: {pdf_resp.headers.get('Content-Type')}")
        
        # Test JSON
        json_resp = requests.get(f"{base_url}/download-report/{scan_id}/?format=json")
        print(f"JSON download status: {json_resp.status_code}")
        print(f"Content-Type: {json_resp.headers.get('Content-Type')}")

if __name__ == "__main__":
    test_flow()
