import os
import re
import time
from .patternLibrary import VULNERABILITY_PATTERNS
from .severityEngine import SeverityEngine

class ScannerEngine:
    # SaaS-level configuration
    # SaaS-level configuration and Aggressive Filtering
    ALLOWED_EXTENSIONS = {'.js', '.ts', '.jsx', '.tsx', '.php', '.py', '.java', '.env', '.json', '.go', '.rb', '.c', '.cpp', '.h', '.cs', '.sh'}
    IGNORED_DIRS = {
        'node_modules', '.git', 'dist', 'build', 'coverage', '.next', '__pycache__',
        'assets', 'images', 'img', 'docs', 'documentation', 'logs', 
        'tmp', 'temp', 'obj', 'bin', '.cache', 'bower_components', 'site-packages'
    }

    def __init__(self, target_path):
        self.target_path = target_path
        self.issues = []
        self.total_files_scanned = 0
        self.start_time = 0

    def scan(self):
        """
        Main scan execution logic.
        """
        self.start_time = time.time()
        print(f"SaaS Scan Started: {self.target_path}")

        # Handle both directory and single file
        if os.path.isfile(self.target_path):
            self._scan_file(self.target_path)
        else:
            self._recursive_scan(self.target_path)

        scan_duration = time.time() - self.start_time
        print(f"Scan Completed in {scan_duration:.2f}s. Files: {self.total_files_scanned}, Issues: {len(self.issues)}")
        
        return self.issues

    def _recursive_scan(self, directory):
        """
        Recursively scans the directory tree.
        """
        for root, dirs, files in os.walk(directory):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS]

            for file in files:
                file_path = os.path.join(root, file)
                self._scan_file(file_path)

    def _scan_file(self, file_path):
        """
        Scans an individual file if it matches allowed extensions.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS and os.path.basename(file_path) != '.env':
            return

        self.total_files_scanned += 1
        
        try:
            # Skip very large files (> 5MB) for performance
            if os.path.getsize(file_path) > 5 * 1024 * 1024:
                print(f"Skipping large file: {file_path}")
                return

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self._apply_patterns(content, file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    def _apply_patterns(self, content, file_path):
        """
        Applies all regex patterns to the file content.
        """
        for pattern in VULNERABILITY_PATTERNS:
            matches = re.finditer(pattern['regex'], content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_idx = content.count('\n', 0, match.start()) + 1
                snippet = self._get_snippet(content, match.start(), match.end())
                
                # Robust relative path calculation
                try:
                    rel_path = os.path.relpath(file_path, self.target_path) if not os.path.isfile(self.target_path) else os.path.basename(file_path)
                except Exception:
                    rel_path = os.path.basename(file_path)

                self.issues.append({
                    'file': rel_path,
                    'line': line_idx,
                    'vulnerabilityType': pattern['type'],
                    'severity': pattern['severity'],
                    'description': pattern['description'],
                    'matchedCode': match.group(0),
                    'solution': pattern['solution'],
                    'snippet': snippet
                })

    def _get_snippet(self, content, start_pos, end_pos, context_lines=2):
        """
        Extracts a snippet of code around the match for reporting.
        """
        # Simple extraction for now
        lines = content.splitlines()
        line_idx = content.count('\n', 0, start_pos)
        
        start_line = max(0, line_idx - context_lines)
        end_line = min(len(lines), line_idx + context_lines + 1)
        
        snippet_lines = []
        for i in range(start_line, end_line):
            prefix = ">> " if i == line_idx else "   "
            snippet_lines.append(f"{prefix}{i+1} | {lines[i]}")
            
        return "\n".join(snippet_lines)
