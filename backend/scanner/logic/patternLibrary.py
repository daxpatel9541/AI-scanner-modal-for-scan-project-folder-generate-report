import re

# SaaS-Level Pattern Library
# Each pattern includes: regex, type, severity, description, and solution

VULNERABILITY_PATTERNS = [
    {
        "id": "sqli",
        "type": "SQL Injection",
        "severity": "CRITICAL",
        "regex": r"(?:SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\s+.*\s+FROM\s+.*(?:\'|\"|\s+OR\s+|\s+AND\s+)",
        "description": "Potential SQL Injection detected. Direct string concatenation in queries can allow attackers to execute arbitrary database commands.",
        "solution": "Use parameterized queries or ORM methods instead of string formatting."
    },
    {
        "id": "xss",
        "type": "Cross-Site Scripting (XSS)",
        "severity": "HIGH",
        "regex": r"(?:\.innerHTML|\.outerHTML)\s*=\s*.*|\.append\(.*<script.*",
        "description": "Potential XSS detected via insecure DOM manipulation. Attackers can inject malicious scripts into the page.",
        "solution": "Use .textContent or .innerText, or properly sanitize HTML before injection."
    },
    {
        "id": "cmd_injection",
        "type": "Command Injection",
        "severity": "CRITICAL",
        "regex": r"(?:child_process\.exec|os\.system|subprocess\.Popen|subprocess\.run)\s*\(.*(?:\'|\"|\s*[;&|]\s*)",
        "description": "Potential Command Injection. Running shell commands with unvalidated input can lead to full server compromise.",
        "solution": "Avoid shell execution. Pass arguments as a list to subprocess.run/exec without shell=True."
    },
    {
        "id": "secrets_stripe",
        "type": "Hardcoded Stripe Secret",
        "severity": "CRITICAL",
        "regex": r"sk_(?:test|live)_[0-9a-zA-Z]{24}",
        "description": "Hardcoded Stripe Secret Key detected. Leaking this allows attackers to process payments or drain funds.",
        "solution": "Move secrets to .env files and use environment variables."
    },
    {
        "id": "secrets_aws",
        "type": "Hardcoded AWS Key",
        "severity": "CRITICAL",
        "regex": r"(?:AKIA|ASYA|ABIA|ACCA)[0-9A-Z]{16}",
        "description": "Hardcoded AWS Access Key detected. Exposure can lead to unauthorized cloud infrastructure access.",
        "solution": "Use IAM roles or environment variables for AWS credentials."
    },
    {
        "id": "secrets_jwt",
        "type": "JWT Secret Exposure",
        "severity": "HIGH",
        "regex": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "description": "Potential JWT secret or token hardcoded. Allows attackers to forge authentication tokens.",
        "solution": "Never hardcode JWT secrets. Store them in a secure secret manager."
    },
    {
        "id": "insecure_eval",
        "type": "Insecure Eval Usage",
        "severity": "CRITICAL",
        "regex": r"(?<![a-zA-Z0-9_])eval\s*\(.*\)",
        "description": "Use of eval() detected. eval() evaluates strings as code, which is extremely dangerous with user input.",
        "solution": "Use JSON.parse() for data or safer alternatives like ast.literal_eval() in Python."
    },
    {
        "id": "unsafe_upload",
        "type": "Unsafe File Upload",
        "severity": "MEDIUM",
        "regex": r"(?:upload|destination)\s*[:=]\s*.*(?:\/tmp\/|uploads\/|public\/)",
        "description": "Potential unsafe file upload path detected. Could lead to path traversal or malware hosting.",
        "solution": "Validate file extensions and use randomized filenames in restricted directories."
    },
    {
        "id": "cors_policy",
        "type": "Open CORS Policy",
        "severity": "MEDIUM",
        "regex": r"(?:Access-Control-Allow-Origin|cors_origin)\s*[:=]\s*[\'\"]\*[\'\"]",
        "description": "Wildcard CORS policy detected (*). Allows any website to interact with your API.",
        "solution": "Restrict allowed origins to specific domains in production."
    }
]
