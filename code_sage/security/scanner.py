"""Security vulnerability scanner."""

import re
import hashlib
import math
from pathlib import Path
from typing import List, Optional, Dict
import subprocess
import json

from code_sage.core.models import Issue, IssueSeverity, IssueCategory, CodeLocation
from code_sage.core.config import Config
from code_sage.core.logger import get_logger
from code_sage.utils.file_utils import read_file


class SecurityScanner:
    """Security vulnerability scanner."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize security scanner.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.logger = get_logger()

    def scan_file(self, file_path: Path) -> List[Issue]:
        """
        Scan file for security issues.

        Args:
            file_path: Path to file

        Returns:
            List of security issues
        """
        issues = []

        try:
            content = read_file(file_path)

            # Run various security checks
            if self.config.security.enable_secrets_scan:
                issues.extend(self._scan_secrets(file_path, content))

            if self.config.security.enable_owasp_scan:
                issues.extend(self._scan_owasp(file_path, content))

            # Language-specific scans
            if file_path.suffix == ".py":
                issues.extend(self._scan_python_security(file_path, content))
            elif file_path.suffix in [".js", ".ts", ".jsx", ".tsx"]:
                issues.extend(self._scan_javascript_security(file_path, content))

        except Exception as e:
            self.logger.error(f"Security scan failed for {file_path}: {e}")

        return issues

    def _scan_secrets(self, file_path: Path, content: str) -> List[Issue]:
        """Scan for hardcoded secrets."""
        issues = []
        lines = content.splitlines()

        # Common secret patterns
        patterns = [
            (r'(aws_access_key_id|AWS_ACCESS_KEY_ID)\s*=\s*["\']?([A-Z0-9]{20})["\']?', "AWS Access Key"),
            (r'(aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*=\s*["\']?([A-Za-z0-9/+=]{40})["\']?', "AWS Secret Key"),
            (r'(github_token|GITHUB_TOKEN)\s*=\s*["\']?(ghp_[A-Za-z0-9]{36})["\']?', "GitHub Token"),
            (r'(api[_-]?key|API[_-]?KEY)\s*=\s*["\']?([A-Za-z0-9_\-]{32,})["\']?', "API Key"),
            (r'(password|PASSWORD|passwd|PASSWD)\s*=\s*["\']([^"\']{8,})["\']', "Hardcoded Password"),
            (r'(private[_-]?key|PRIVATE[_-]?KEY)\s*=\s*["\']([^"\']+)["\']', "Private Key"),
            (r'(-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----)', "RSA Private Key"),
        ]

        for line_num, line in enumerate(lines, start=1):
            for pattern, secret_type in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Check entropy of the matched string
                    secret_value = match.group(2) if len(match.groups()) > 1 else match.group(1)
                    entropy = self._calculate_entropy(secret_value)

                    if entropy >= self.config.security.min_entropy_threshold:
                        issues.append(
                            Issue(
                                id=self._generate_issue_id(file_path, "secret", line_num),
                                title=f"Hardcoded Secret: {secret_type}",
                                description=f"Potential hardcoded {secret_type.lower()} detected",
                                severity=IssueSeverity.CRITICAL,
                                category=IssueCategory.SECURITY,
                                location=CodeLocation(
                                    file_path=str(file_path),
                                    line_start=line_num,
                                    line_end=line_num,
                                ),
                                code_snippet=self._get_snippet(lines, line_num),
                                suggested_fix="Store secrets in environment variables or use a secrets management service",
                                auto_fixable=False,
                            )
                        )

        return issues

    def _scan_owasp(self, file_path: Path, content: str) -> List[Issue]:
        """Scan for OWASP Top 10 vulnerabilities."""
        issues = []
        lines = content.splitlines()

        # SQL Injection patterns
        sql_patterns = [
            (r'(execute|query|run)\s*\([^)]*\+[^)]*\)', "SQL Injection via string concatenation"),
            (r'(SELECT|INSERT|UPDATE|DELETE).*%s.*%', "SQL Injection via string formatting"),
            (r'f["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?\{', "SQL Injection via f-string"),
        ]

        # XSS patterns
        xss_patterns = [
            (r'innerHTML\s*=\s*.*(?!sanitize)', "Potential XSS via innerHTML"),
            (r'document\.write\s*\(', "Potential XSS via document.write"),
            (r'eval\s*\(', "Code Injection via eval"),
        ]

        # Command Injection patterns
        command_patterns = [
            (r'(exec|system|popen|subprocess\.(?:call|run|Popen))\s*\([^)]*\+', "Command Injection via concatenation"),
            (r'(os\.system|os\.popen|subprocess\.(?:call|run))\s*\(.*shell\s*=\s*True', "Shell Command Injection risk"),
        ]

        all_patterns = [
            (sql_patterns, "SQL Injection"),
            (xss_patterns, "Cross-Site Scripting (XSS)"),
            (command_patterns, "Command Injection"),
        ]

        for patterns, category_name in all_patterns:
            for line_num, line in enumerate(lines, start=1):
                for pattern, description in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(
                            Issue(
                                id=self._generate_issue_id(file_path, category_name, line_num),
                                title=category_name,
                                description=description,
                                severity=IssueSeverity.HIGH,
                                category=IssueCategory.SECURITY,
                                location=CodeLocation(
                                    file_path=str(file_path),
                                    line_start=line_num,
                                    line_end=line_num,
                                ),
                                code_snippet=self._get_snippet(lines, line_num),
                                auto_fixable=False,
                            )
                        )

        return issues

    def _scan_python_security(self, file_path: Path, content: str) -> List[Issue]:
        """Python-specific security checks."""
        issues = []
        lines = content.splitlines()

        patterns = [
            (r'pickle\.loads?\(', "Unsafe Pickle Deserialization", IssueSeverity.HIGH),
            (r'yaml\.load\([^,)]*\)', "Unsafe YAML Deserialization", IssueSeverity.HIGH),
            (r'input\s*\([^)]*\)', "Use of input() can be dangerous", IssueSeverity.LOW),
            (r'random\.random\(\)', "Weak Random Number Generation", IssueSeverity.MEDIUM),
        ]

        for line_num, line in enumerate(lines, start=1):
            for pattern, title, severity in patterns:
                if re.search(pattern, line):
                    issues.append(
                        Issue(
                            id=self._generate_issue_id(file_path, title, line_num),
                            title=title,
                            description=f"Security issue detected: {title}",
                            severity=severity,
                            category=IssueCategory.SECURITY,
                            location=CodeLocation(
                                file_path=str(file_path),
                                line_start=line_num,
                                line_end=line_num,
                            ),
                            code_snippet=self._get_snippet(lines, line_num),
                            auto_fixable=False,
                        )
                    )

        return issues

    def _scan_javascript_security(self, file_path: Path, content: str) -> List[Issue]:
        """JavaScript-specific security checks."""
        issues = []
        lines = content.splitlines()

        patterns = [
            (r'dangerouslySetInnerHTML', "Dangerous React Property", IssueSeverity.HIGH),
            (r'eval\s*\(', "Use of eval()", IssueSeverity.HIGH),
            (r'Function\s*\(', "Dynamic Function Construction", IssueSeverity.MEDIUM),
            (r'localStorage\.setItem.*password', "Password in LocalStorage", IssueSeverity.CRITICAL),
        ]

        for line_num, line in enumerate(lines, start=1):
            for pattern, title, severity in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        Issue(
                            id=self._generate_issue_id(file_path, title, line_num),
                            title=title,
                            description=f"Security issue detected: {title}",
                            severity=severity,
                            category=IssueCategory.SECURITY,
                            location=CodeLocation(
                                file_path=str(file_path),
                                line_start=line_num,
                                line_end=line_num,
                            ),
                            code_snippet=self._get_snippet(lines, line_num),
                            auto_fixable=False,
                        )
                    )

        return issues

    def _calculate_entropy(self, string: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not string:
            return 0.0

        entropy = 0.0
        for char in set(string):
            prob = string.count(char) / len(string)
            entropy -= prob * math.log2(prob)

        return entropy

    def _get_snippet(self, lines: List[str], line_num: int, context: int = 2) -> str:
        """Get code snippet with context."""
        start = max(0, line_num - 1 - context)
        end = min(len(lines), line_num + context)

        snippet_lines = []
        for i in range(start, end):
            prefix = "→ " if i == line_num - 1 else "  "
            snippet_lines.append(f"{prefix}{i + 1:4d} | {lines[i]}")

        return "\n".join(snippet_lines)

    def _generate_issue_id(self, file_path: Path, issue_type: str, line: int) -> str:
        """Generate unique issue ID."""
        data = f"{file_path}:{issue_type}:{line}"
        return hashlib.md5(data.encode()).hexdigest()[:12]


class DependencyScanner:
    """Scan dependencies for known vulnerabilities."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize dependency scanner."""
        self.config = config or Config()
        self.logger = get_logger()

    def scan_dependencies(self, project_path: Path) -> List[Issue]:
        """
        Scan project dependencies.

        Args:
            project_path: Path to project

        Returns:
            List of dependency issues
        """
        issues = []

        # Check for Python requirements.txt
        requirements_file = project_path / "requirements.txt"
        if requirements_file.exists():
            issues.extend(self._scan_python_deps(requirements_file))

        # Check for package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            issues.extend(self._scan_npm_deps(package_json))

        return issues

    def _scan_python_deps(self, requirements_file: Path) -> List[Issue]:
        """Scan Python dependencies."""
        issues = []

        try:
            # Use safety to check for known vulnerabilities
            result = subprocess.run(
                ["safety", "check", "--file", str(requirements_file), "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout:
                vulnerabilities = json.loads(result.stdout)
                for vuln in vulnerabilities:
                    issues.append(
                        Issue(
                            id=hashlib.md5(f"{vuln['package']}{vuln['id']}".encode()).hexdigest()[:12],
                            title=f"Vulnerable Dependency: {vuln['package']}",
                            description=vuln.get("advisory", "Known vulnerability"),
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.SECURITY,
                            location=CodeLocation(
                                file_path=str(requirements_file),
                                line_start=1,
                                line_end=1,
                            ),
                            suggested_fix=f"Update to version {vuln.get('fixed_version', 'latest')}",
                            auto_fixable=False,
                        )
                    )

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.debug(f"Could not scan Python dependencies: {e}")

        return issues

    def _scan_npm_deps(self, package_json: Path) -> List[Issue]:
        """Scan NPM dependencies."""
        issues = []

        try:
            # Use npm audit
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=package_json.parent,
                timeout=30,
            )

            if result.stdout:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get("vulnerabilities", {})

                for pkg_name, vuln_data in vulnerabilities.items():
                    severity_map = {
                        "critical": IssueSeverity.CRITICAL,
                        "high": IssueSeverity.HIGH,
                        "moderate": IssueSeverity.MEDIUM,
                        "low": IssueSeverity.LOW,
                    }

                    severity = severity_map.get(
                        vuln_data.get("severity", "medium"), IssueSeverity.MEDIUM
                    )

                    issues.append(
                        Issue(
                            id=hashlib.md5(f"{pkg_name}".encode()).hexdigest()[:12],
                            title=f"Vulnerable NPM Package: {pkg_name}",
                            description=vuln_data.get("via", ["Known vulnerability"])[0]
                            if isinstance(vuln_data.get("via"), list)
                            else "Known vulnerability",
                            severity=severity,
                            category=IssueCategory.SECURITY,
                            location=CodeLocation(
                                file_path=str(package_json),
                                line_start=1,
                                line_end=1,
                            ),
                            auto_fixable=False,
                        )
                    )

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.debug(f"Could not scan NPM dependencies: {e}")

        return issues
