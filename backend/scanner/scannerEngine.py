import os
import re
import time
from .patternLibrary import VULNERABILITY_PATTERNS
from .severityEngine import SeverityEngine

class ScannerEngine:
    # SaaS-level configuration
    # SaaS-level configuration and Aggressive Filtering
    ALLOWED_EXTENSIONS = {'.js', '.ts', '.jsx', '.tsx', '.php', '.py', '.java', '.env', '.json', '.go', '.rb', '.c', '.cpp', '.h', '.cs', '.sh', '.yml', '.yaml'}
    IGNORED_DIRS = {
        'node_modules', '.git', 'dist', 'build', 'coverage', '.next', '__pycache__',
        'assets', 'images', 'img', 'docs', 'documentation', 'logs', 
        'tmp', 'temp', 'obj', 'bin', '.cache', 'bower_components', 'site-packages',
        'venv', '.venv', 'env', '.env', '.vscode', '.idea'
    }

    def __init__(self, target_path):
        self.target_path = target_path
        self.issues = []
        self.total_files_scanned = 0
        self.start_time = 0

    def scan(self):
        """
        Main scan execution logic with performance protection.
        """
        self.start_time = time.time()
        print(f"SaaS Scan Started: {self.target_path}")

        try:
            if os.path.isfile(self.target_path):
                self._scan_file(self.target_path)
            else:
                self._recursive_scan(self.target_path)
        except Exception as e:
            print(f"Scan interrupted: {e}")

        scan_duration = time.time() - self.start_time
        print(f"Scan Completed in {scan_duration:.2f}s. Files: {self.total_files_scanned}, Issues: {len(self.issues)}")
        
        return self.issues

    def _recursive_scan(self, directory):
        """
        Recursively scans the directory tree, pruning ignored folders.
        """
        for root, dirs, files in os.walk(directory):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS and not d.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                self._scan_file(file_path)

    def _is_binary(self, file_path):
        """
        Check if a file is binary by reading a small chunk.
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True

    def _scan_file(self, file_path):
        """
        Scans an individual file if it matches allowed extensions and isn't binary.
        """
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Security: Always scan .env even if ext logic differs
        if ext not in self.ALLOWED_EXTENSIONS and filename != '.env':
            return

        if self._is_binary(file_path):
            return

        self.total_files_scanned += 1
        
        try:
            # Performance: File size limit (5MB)
            if os.path.getsize(file_path) > 5 * 1024 * 1024:
                print(f"Skipping large file: {file_path}")
                return

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if content:
                    self._apply_patterns(content, file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    def _apply_patterns(self, content, file_path):
        """
        Applies all regex patterns to the file content with accurate line tracking.
        """
        # Pre-split lines for faster snippet extraction and line counting
        lines = content.splitlines()
        
        for pattern in VULNERABILITY_PATTERNS:
            # Use re.DOTALL if needed, but here we usually scan line-by-line or with re.MULTILINE
            matches = re.finditer(pattern['regex'], content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Calculate line number
                line_idx = content.count('\n', 0, match.start()) + 1
                matched_code = match.group(0).strip()
                
                if not matched_code: continue # Avoid empty matches

                snippet = self._get_snippet(lines, line_idx)
                
                try:
                    rel_path = os.path.relpath(file_path, self.target_path) if not os.path.isfile(self.target_path) else os.path.basename(file_path)
                except Exception:
                    rel_path = os.path.basename(file_path)

                issue = {
                    'file': rel_path,
                    'line': line_idx,
                    'vulnerabilityType': pattern['type'],
                    'severity': pattern['severity'],
                    'description': pattern['description'],
                    'matchedCode': matched_code,
                    'solution': pattern['solution'],
                    'snippet': snippet
                }
                
                # De-deduplication
                if issue not in self.issues:
                    self.issues.append(issue)

    def _get_snippet(self, lines, line_idx, context_lines=2):
        """
        Extracts a snippet of code around the match for reporting.
        """
        actual_idx = line_idx - 1
        start_line = max(0, actual_idx - context_lines)
        end_line = min(len(lines), actual_idx + context_lines + 1)
        
        snippet_lines = []
        for i in range(start_line, end_line):
            prefix = ">> " if i == actual_idx else "   "
            # Ensure line exists in array (safety)
            if i < len(lines):
                snippet_lines.append(f"{prefix}{i+1} | {lines[i]}")
            
        return "\n".join(snippet_lines)
