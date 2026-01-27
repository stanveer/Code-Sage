"""Pattern matching engine for detecting code issues."""

import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Pattern
from dataclasses import dataclass

from code_sage.core.models import Issue, IssueSeverity, IssueCategory, CodeLocation
from code_sage.core.logger import get_logger


@dataclass
class PatternRule:
    """Pattern rule definition."""

    id: str
    name: str
    description: str
    pattern: str
    severity: IssueSeverity
    category: IssueCategory
    languages: List[str]
    message: str
    fix_suggestion: Optional[str] = None
    auto_fixable: bool = False
    flags: int = 0


class PatternMatcher:
    """Pattern matching engine for code analysis."""

    def __init__(self) -> None:
        """Initialize pattern matcher."""
        self.logger = get_logger()
        self.rules: List[PatternRule] = []
        self._compiled_patterns: Dict[str, Pattern] = {}
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load default pattern rules."""
        default_rules = [
            # Security patterns
            PatternRule(
                id="hardcoded-password",
                name="Hardcoded Password",
                description="Potential hardcoded password detected",
                pattern=r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.SECURITY,
                languages=["python", "javascript", "typescript", "java"],
                message="Hardcoded password detected. Use environment variables or secrets management.",
                fix_suggestion="Store passwords in environment variables or use a secrets management service",
                flags=re.IGNORECASE,
            ),
            PatternRule(
                id="hardcoded-api-key",
                name="Hardcoded API Key",
                description="Potential hardcoded API key detected",
                pattern=r'(api[_-]?key|apikey|access[_-]?key)\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.SECURITY,
                languages=["python", "javascript", "typescript", "java", "go"],
                message="Hardcoded API key detected",
                fix_suggestion="Use environment variables or a secrets manager",
                flags=re.IGNORECASE,
            ),
            PatternRule(
                id="sql-string-concat",
                name="SQL String Concatenation",
                description="SQL query built with string concatenation",
                pattern=r'(SELECT|INSERT|UPDATE|DELETE).*\+.*["\']',
                severity=IssueSeverity.HIGH,
                category=IssueCategory.SECURITY,
                languages=["python", "javascript", "typescript", "java", "php"],
                message="SQL injection vulnerability: Use parameterized queries",
                fix_suggestion="Use parameterized queries or an ORM",
                flags=re.IGNORECASE,
            ),
            # Code quality patterns
            PatternRule(
                id="debug-print",
                name="Debug Print Statement",
                description="Debug print statement found",
                pattern=r'(print|console\.log|System\.out\.println)\(',
                severity=IssueSeverity.LOW,
                category=IssueCategory.CODE_SMELL,
                languages=["python", "javascript", "typescript", "java"],
                message="Debug print statement should be removed or replaced with proper logging",
                fix_suggestion="Use a logging library instead of print statements",
                auto_fixable=True,
            ),
            PatternRule(
                id="todo-comment",
                name="TODO Comment",
                description="TODO comment found",
                pattern=r'#\s*TODO|//\s*TODO|/\*\s*TODO',
                severity=IssueSeverity.INFO,
                category=IssueCategory.MAINTAINABILITY,
                languages=["python", "javascript", "typescript", "java", "go", "rust"],
                message="TODO comment found - consider creating a task or issue",
                flags=re.IGNORECASE,
            ),
            PatternRule(
                id="fixme-comment",
                name="FIXME Comment",
                description="FIXME comment found",
                pattern=r'#\s*FIXME|//\s*FIXME|/\*\s*FIXME',
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.BUG,
                languages=["python", "javascript", "typescript", "java", "go", "rust"],
                message="FIXME comment indicates a known issue that needs attention",
                flags=re.IGNORECASE,
            ),
            # Best practices
            PatternRule(
                id="except-pass",
                name="Empty Exception Handler",
                description="Exception caught but not handled",
                pattern=r'except.*:\s*pass',
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.BEST_PRACTICE,
                languages=["python"],
                message="Empty exception handler - at least log the error",
                fix_suggestion="Add logging or proper error handling",
            ),
            PatternRule(
                id="catch-empty",
                name="Empty Catch Block",
                description="Exception caught but not handled",
                pattern=r'catch\s*\([^)]+\)\s*\{\s*\}',
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.BEST_PRACTICE,
                languages=["javascript", "typescript", "java"],
                message="Empty catch block - at least log the error",
                fix_suggestion="Add logging or proper error handling",
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def add_rule(self, rule: PatternRule) -> None:
        """
        Add a pattern rule.

        Args:
            rule: PatternRule to add
        """
        self.rules.append(rule)
        try:
            self._compiled_patterns[rule.id] = re.compile(rule.pattern, rule.flags)
        except re.error as e:
            self.logger.error(f"Invalid regex pattern in rule {rule.id}: {e}")

    def match_file(self, file_path: Path, content: str, language: str) -> List[Issue]:
        """
        Match patterns in file content.

        Args:
            file_path: Path to file
            content: File content
            language: Programming language

        Returns:
            List of issues found
        """
        issues = []
        lines = content.splitlines()

        for rule in self.rules:
            # Skip if language not supported by this rule
            if language not in rule.languages:
                continue

            pattern = self._compiled_patterns.get(rule.id)
            if not pattern:
                continue

            # Search each line
            for line_num, line in enumerate(lines, start=1):
                matches = pattern.finditer(line)
                for match in matches:
                    issue = Issue(
                        id=self._generate_issue_id(file_path, rule.id, line_num),
                        title=rule.name,
                        description=rule.message,
                        severity=rule.severity,
                        category=rule.category,
                        location=CodeLocation(
                            file_path=str(file_path),
                            line_start=line_num,
                            line_end=line_num,
                            column_start=match.start(),
                            column_end=match.end(),
                        ),
                        code_snippet=self._get_snippet(lines, line_num),
                        suggested_fix=rule.fix_suggestion,
                        auto_fixable=rule.auto_fixable,
                        rule_id=rule.id,
                    )
                    issues.append(issue)

        return issues

    def _get_snippet(self, lines: List[str], line_num: int, context: int = 2) -> str:
        """Get code snippet with context."""
        start = max(0, line_num - 1 - context)
        end = min(len(lines), line_num + context)

        snippet_lines = []
        for i in range(start, end):
            prefix = "→ " if i == line_num - 1 else "  "
            snippet_lines.append(f"{prefix}{i + 1:4d} | {lines[i]}")

        return "\n".join(snippet_lines)

    def _generate_issue_id(self, file_path: Path, rule_id: str, line: int) -> str:
        """Generate unique issue ID."""
        data = f"{file_path}:{rule_id}:{line}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def load_custom_rules(self, rules_file: Path) -> None:
        """
        Load custom rules from a file.

        Args:
            rules_file: Path to rules file (JSON or YAML)
        """
        import json
        import yaml

        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                if rules_file.suffix == ".json":
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            for rule_data in data.get("rules", []):
                rule = PatternRule(
                    id=rule_data["id"],
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    pattern=rule_data["pattern"],
                    severity=IssueSeverity(rule_data.get("severity", "medium")),
                    category=IssueCategory(rule_data.get("category", "code_smell")),
                    languages=rule_data.get("languages", []),
                    message=rule_data.get("message", ""),
                    fix_suggestion=rule_data.get("fix_suggestion"),
                    auto_fixable=rule_data.get("auto_fixable", False),
                )
                self.add_rule(rule)

            self.logger.info(f"Loaded custom rules from {rules_file}")

        except Exception as e:
            self.logger.error(f"Failed to load custom rules: {e}")
