import re

# SaaS-Level Pattern Library
# Each pattern includes: regex, type, severity, description, and solution

VULNERABILITY_PATTERNS = [
    {
        "id": "sqli",
        "type": "SQL Injection",
        "severity": "CRITICAL",
        "regex": r"(?i)(?:SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|EXEC|EXECUTE)\s+.*\s+(?:FROM|INTO|SET|TABLE|WHERE)\s+.*(?:['\"]|\+\s*\w|\.format\(|f['\"]|%s|\?\s*)",
        "description": "Potential SQL Injection detected. Using string concatenation, interpolation, or direct formatting in database queries can allow attackers to execute arbitrary commands.",
        "solution": "Use parameterized queries (e.g., cursor.execute('... WHERE id = %s', [id])) or ORM methods (e.g., User.objects.get(id=id))."
    },
    {
        "id": "nosqli",
        "type": "NoSQL Injection",
        "severity": "HIGH",
        "regex": r"(?i)\$\s*(?:where|ne|gt|lt|regex|expr)|\.(?:find|update|remove|aggregate)\s*\(\s*\{\s*.*\$.*\}",
        "description": "Potential NoSQL Injection detected. Unvalidated input in NoSQL queries can allow attackers to bypass security checks or extract data.",
        "solution": "Sanitize input for operator characters (e.g., $) and avoid using where/regex operators with user-provided strings."
    },
    {
        "id": "xss",
        "type": "Cross-Site Scripting (XSS)",
        "severity": "HIGH",
        "regex": r"(?i)(?:\.innerHTML|\.outerHTML)\s*=\s*(?:['\"]|\w)|(?:document\.write|document\.writeln)\(.*\)|(?:\.append|\.prepend)\(.*<script.*",
        "description": "Potential XSS detected via insecure DOM manipulation. Direct assignment to innerHTML or document.write can lead to script injection.",
        "solution": "Use .textContent or .innerText for plain text. Use a dedicated sanitization library (e.g., DOMPurify) if HTML injection is necessary."
    },
    {
        "id": "cmd_injection",
        "type": "Command Injection",
        "severity": "CRITICAL",
        "regex": r"(?i)(?:os\.system|subprocess\.Popen|subprocess\.run|subprocess\.call|subprocess\.check_call|subprocess\.check_output|child_process\.exec|child_process\.spawn)\s*\(.*shell\s*=\s*True.*|(?:\bspawn\b|\bexec\b)\s*\(.*(?:['\"]|\$|\{|\w)",
        "description": "Potential Command Injection. Running shell commands with unvalidated input or shell=True can lead to full server compromise.",
        "solution": "Avoid shell=True. Pass arguments as a list (e.g., subprocess.run(['ls', '-l'])) and avoid using shell metacharacters in input."
    },
    {
        "id": "secrets_stripe",
        "type": "Hardcoded Stripe Secret",
        "severity": "CRITICAL",
        "regex": r"sk_(?:test|live)_[0-9a-zA-Z]{24}",
        "description": "Hardcoded Stripe Secret Key detected. This allows unauthorized access to your Stripe account.",
        "solution": "Move secrets to environment variables or a secret manager."
    },
    {
        "id": "secrets_aws",
        "type": "Hardcoded AWS Key",
        "severity": "CRITICAL",
        "regex": r"(?i)(?:AKIA|ASYA|ABIA|ACCA)[0-9A-Z]{16}\b",
        "description": "Hardcoded AWS Access Key detected. Exposure can lead to unauthorized cloud infrastructure access.",
        "solution": "Use IAM roles for services or store credentials in environment variables."
    },
    {
        "id": "secrets_aws_secret",
        "type": "Hardcoded AWS Secret",
        "severity": "CRITICAL",
        "regex": r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])",
        "description": "Hardcoded AWS Secret Key detected.",
        "solution": "Use IAM roles or environment variables."
    },
    {
        "id": "secrets_jwt",
        "type": "JWT Secret Exposure",
        "severity": "HIGH",
        "regex": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "description": "Potential JWT secret or token hardcoded. Allows attackers to forge authentication tokens.",
        "solution": "Store JWT secrets in a secure secret manager."
    },
    {
        "id": "insecure_eval",
        "type": "Insecure Eval/Exec Usage",
        "severity": "CRITICAL",
        "regex": r"(?<![a-zA-Z0-9_])(?:eval|exec)\s*\(.*\)",
        "description": "Use of eval() or exec() detected. These functions evaluate strings as code, which is extremely dangerous with user input.",
        "solution": "Use safer alternatives like ast.literal_eval() for data, or JSON.parse() in JS."
    },
    {
        "id": "weak_crypto",
        "type": "Weak Cryptography",
        "severity": "MEDIUM",
        "regex": r"(?i)\b(?:md5|sha1)\b(?!\.js|\.py)|hashlib\.(?:md5|sha1)\(.*\)",
        "description": "Use of weak hashing algorithms (MD5/SHA1) detected. These are vulnerable to collision attacks.",
        "solution": "Use stronger algorithms like SHA-256 or bcrypt for password hashing."
    },
    {
        "id": "insecure_cookie",
        "type": "Insecure Cookie Settings",
        "severity": "MEDIUM",
        "regex": r"(?i)cookie\s*(?:[:=]|\.set).*secure\s*[:=]\s*false|(?i)cookie\s*(?:[:=]|\.set).*httpOnly\s*[:=]\s*false",
        "description": "Insecure cookie settings (Secure=false or HttpOnly=false).",
        "solution": "Set Secure=true and HttpOnly=true for all sensitive cookies."
    },
    {
        "id": "cors_policy",
        "type": "Wildcard CORS Policy",
        "severity": "MEDIUM",
        "regex": r"(?i)(?:Access-Control-Allow-Origin|cors_origin)\s*[:=]\s*['\"]\*['\"]",
        "description": "Wildcard CORS policy detected (*). Allows any origin to access your resources.",
        "solution": "Restrict allowed origins to specific trusted domains."
    }
]
