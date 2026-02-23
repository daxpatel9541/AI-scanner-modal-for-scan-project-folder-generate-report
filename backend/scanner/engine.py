import os
import zipfile
import subprocess
import json
import tempfile
import shutil

def run_bandit_scan(folder_path):
    """
    Runs Bandit on the specified folder.
    """
    try:
        print(f"Starting Bandit scan on: {folder_path}")
        result = subprocess.run(
            ['python', '-m', 'bandit', '-r', folder_path, '-f', 'json'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stderr:
            print(f"Bandit stderr: {result.stderr}")
            
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                issues = data.get('results', [])
                print(f"Bandit found {len(issues)} issues.")
                return issues
            except json.JSONDecodeError:
                print("Failed to parse Bandit JSON output.")
        return []
    except Exception as e:
        print(f"Error running Bandit: {e}")
        return []

def run_semgrep_scan(folder_path):
    """
    Runs Semgrep on the specified folder for multi-language support.
    """
    try:
        print(f"Starting Semgrep scan on: {folder_path}")
        # Using 'auto' config for default security rules
        result = subprocess.run(
            ['python', '-m', 'semgrep', 'scan', '--config', 'auto', '--json', folder_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stderr:
            print(f"Semgrep stderr: {result.stderr}")
            
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                issues = data.get('results', [])
                print(f"Semgrep found {len(issues)} issues.")
                return issues
            except json.JSONDecodeError:
                print("Failed to parse Semgrep JSON output.")
        return []
    except Exception as e:
        print(f"Error running Semgrep: {e}")
        return []

def ai_intelligence_layer(vulnerability):
    """
    Simulates AI-driven contextual analysis.
    In a production app, this would call an LLM (OpenAI, Claude, etc.)
    """
    v_type = vulnerability.get('type', 'Unknown')
    # Mock AI logic based on vulnerability type
    explanations = {
        "eval": "Critical: The use of 'eval()' allows execution of arbitrary strings as code. This can lead to full system compromise if user input is passed.",
        "os.system": "Critical: Using 'os.system' with unvalidated input permits Command Injection. An attacker could execute arbitrary shell commands.",
        "hardcoded_secret": "High: Exposed secrets in source code can be leaked to unauthorized parties, leading to credential theft.",
        "xss": "High: Cross-Site Scripting allows attackers to inject malicious scripts into web pages viewed by other users."
    }
    
    suggestion = explanations.get(v_type.lower(), "AI Suggestion: Review the code for insecure patterns and follow OWASP best practices for input validation and output encoding.")
    return suggestion

def aggregate_scan_results(zip_file_path):
    """
    Extracts ZIP, runs multiple scanners, applies AI analysis, and aggregates results.
    """
    temp_dir = tempfile.mkdtemp()
    aggregated_results = []
    
    try:
        print(f"Processing ZIP: {zip_file_path}")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Verify extracted content
        extracted_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                extracted_files.append(os.path.join(root, file))
        print(f"Extracted {len(extracted_files)} files for analysis.")

        if not extracted_files:
            print("Warning: No files found in ZIP after extraction.")
            return []

        # 1. Run Bandit (Python)
        bandit_issues = run_bandit_scan(temp_dir)
        for issue in bandit_issues:
            aggregated_results.append({
                'file': os.path.relpath(issue.get('filename'), temp_dir),
                'line': issue.get('line_number'),
                'type': issue.get('issue_text'),
                'severity': issue.get('issue_severity'),
                'scanner': 'Bandit',
                'ai_explanation': ai_intelligence_layer({'type': 'eval' if 'eval' in issue.get('issue_text').lower() else 'unknown'})
            })

        # 2. Run Semgrep (Multi-language)
        semgrep_issues = run_semgrep_scan(temp_dir)
        for issue in semgrep_issues:
            # Map Semgrep fields properly
            extra = issue.get('extra', {})
            aggregated_results.append({
                'file': os.path.relpath(issue.get('path'), temp_dir),
                'line': issue.get('start', {}).get('line'),
                'type': extra.get('message'),
                'severity': extra.get('severity'),
                'scanner': 'Semgrep',
                'ai_explanation': ai_intelligence_layer({'type': 'xss' if 'xss' in extra.get('message', '').lower() else 'unknown'})
            })

        print(f"Aggregated {len(aggregated_results)} total vulnerabilities.")
        return aggregated_results
    finally:
        shutil.rmtree(temp_dir)
