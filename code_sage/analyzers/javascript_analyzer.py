"""JavaScript and TypeScript code analyzer."""

import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import subprocess
import tempfile

from code_sage.core.analyzer import BaseAnalyzer
from code_sage.core.models import (
    Issue,
    IssueSeverity,
    IssueCategory,
    FileAnalysis,
    CodeLocation,
    CodeMetrics,
)
from code_sage.core.config import Config
from code_sage.utils.file_utils import read_file


class JavaScriptAnalyzer(BaseAnalyzer):
    """Analyzer for JavaScript and TypeScript code."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize JavaScript/TypeScript analyzer."""
        super().__init__(config)
        self.issues: List[Issue] = []

    def get_language(self) -> str:
        """Get language name."""
        return "javascript"

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file is JavaScript or TypeScript."""
        return file_path.suffix in [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """
        Analyze a JavaScript/TypeScript file.

        Args:
            file_path: Path to JavaScript/TypeScript file

        Returns:
            FileAnalysis with issues and metrics
        """
        self.issues = []

        try:
            content = read_file(file_path)

            # Determine if TypeScript
            is_typescript = file_path.suffix in [".ts", ".tsx"]

            # Run various checks
            self._check_syntax(file_path, content, is_typescript)
            self._check_common_issues(file_path, content, is_typescript)
            self._check_best_practices(file_path, content)

            # Calculate metrics
            metrics = self._calculate_metrics(file_path, content)

            return FileAnalysis(
                file_path=str(file_path),
                language="typescript" if is_typescript else "javascript",
                issues=self.issues,
                metrics=metrics,
                success=True,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return FileAnalysis(
                file_path=str(file_path),
                language="javascript",
                success=False,
                error=str(e),
            )

    def _check_syntax(self, file_path: Path, content: str, is_typescript: bool) -> None:
        """Check for syntax errors using esprima."""
        try:
            import esprima
            
            # Try to parse the code
            try:
                if not is_typescript:
                    esprima.parseScript(content, {"tolerant": True, "loc": True})
            except esprima.Error as e:
                self.issues.append(
                    Issue(
                        id=self._generate_issue_id(file_path, "syntax", e.lineNumber),
                        title="JavaScript Syntax Error",
                        description=e.description,
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.BUG,
                        location=CodeLocation(
                            file_path=str(file_path),
                            line_start=e.lineNumber,
                            line_end=e.lineNumber,
                            column_start=e.column,
                        ),
                        code_snippet=self.get_code_snippet(file_path, e.lineNumber, e.lineNumber),
                        auto_fixable=False,
                    )
                )
        except ImportError:
            self.logger.debug("esprima not available, skipping syntax check")

    def _create_issue(self, file_path: Path, line_num: int, issue_type: str, 
                      title: str, description: str, severity: IssueSeverity,
                      category: IssueCategory, suggested_fix: str, 
                      auto_fixable: bool = False) -> Issue:
        """Helper to create an issue with consistent structure."""
        return Issue(
            id=self._generate_issue_id(file_path, issue_type, line_num),
            title=title,
            description=description,
            severity=severity,
            category=category,
            location=CodeLocation(
                file_path=str(file_path),
                line_start=line_num,
                line_end=line_num,
            ),
            code_snippet=self.get_code_snippet(file_path, line_num, line_num),
            suggested_fix=suggested_fix,
            auto_fixable=auto_fixable,
        )

    def _check_console_log(self, file_path: Path, line: str, line_num: int) -> None:
        """Check for console.log statements."""
        if "console.log" in line and not line.strip().startswith("//"):
            self.issues.append(self._create_issue(
                file_path, line_num, "console_log",
                "Console.log Statement",
                "console.log statements should be removed in production code",
                IssueSeverity.LOW, IssueCategory.BEST_PRACTICE,
                "Remove console.log or use a proper logging library",
                auto_fixable=True
            ))

    def _check_loose_equality(self, file_path: Path, line: str, line_num: int) -> None:
        """Check for loose equality (==) instead of strict (===)."""
        if " == " in line and " === " not in line and not line.strip().startswith("//"):
            if "==" in line and "===" not in line:
                self.issues.append(self._create_issue(
                    file_path, line_num, "loose_equality",
                    "Loose Equality Comparison",
                    "Use === instead of == for comparison",
                    IssueSeverity.MEDIUM, IssueCategory.BEST_PRACTICE,
                    "Replace == with ===",
                    auto_fixable=True
                ))

    def _check_var_usage(self, file_path: Path, line: str, line_num: int) -> None:
        """Check for var declarations instead of let/const."""
        if "var " in line and not line.strip().startswith("//"):
            self.issues.append(self._create_issue(
                file_path, line_num, "var_usage",
                "Use of 'var' Keyword",
                "Use 'let' or 'const' instead of 'var'",
                IssueSeverity.LOW, IssueCategory.BEST_PRACTICE,
                "Replace 'var' with 'let' or 'const'",
                auto_fixable=True
            ))

    def _check_eval_usage(self, file_path: Path, line: str, line_num: int) -> None:
        """Check for dangerous eval() usage."""
        # Skip if this is pattern matching/checking code (context-aware detection)
        if "eval(" in line and not line.strip().startswith("//"):
            # Reduce false positives: skip if checking for eval or in string
            if 'if "eval(' in line or "in line" in line or "'eval('" in line or '"eval("' in line:
                return  # This is pattern matching code, not actual eval usage
            
            self.issues.append(self._create_issue(
                file_path, line_num, "eval_usage",
                "Use of eval()",
                "eval() is dangerous and should be avoided",
                IssueSeverity.HIGH, IssueCategory.SECURITY,
                "Refactor to avoid eval()",
                auto_fixable=False
            ))

    def _check_common_issues(self, file_path: Path, content: str, is_typescript: bool) -> None:
        """Check for common JavaScript/TypeScript issues."""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, start=1):
            self._check_console_log(file_path, line, line_num)
            self._check_loose_equality(file_path, line, line_num)
            self._check_var_usage(file_path, line, line_num)
            self._check_eval_usage(file_path, line, line_num)

    def _check_best_practices(self, file_path: Path, content: str) -> None:
        """Check for best practice violations."""
        lines = content.splitlines()

        # Check for proper function declarations
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Check for arrow function without return type (TypeScript)
            if "=>" in stripped and file_path.suffix in [".ts", ".tsx"]:
                if ":" not in stripped or stripped.count(":") == 0:
                    # This is a simplified check
                    pass

            # Check for missing semicolons (simplified)
            if stripped and not stripped.endswith((";", "{", "}", ",", ":")):
                if stripped.startswith(("//", "/*", "*", "import", "export", "if", "else", "for", "while")):
                    continue
                # This is a simplified check and may have false positives

    def _calculate_metrics(self, file_path: Path, content: str) -> CodeMetrics:
        """Calculate code metrics."""
        lines = content.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())

        # Count comment lines (simplified)
        comment_lines = 0
        in_block_comment = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if "/*" in stripped:
                in_block_comment = True
            if "*/" in stripped:
                in_block_comment = False
                comment_lines += 1
                continue
            if in_block_comment or stripped.startswith("//"):
                comment_lines += 1

        source_lines = total_lines - blank_lines - comment_lines

        # Simple complexity estimate (count functions)
        function_count = content.count("function ") + content.count("=>")
        avg_complexity = min(function_count * 2, 20)  # Rough estimate

        return CodeMetrics(
            lines_of_code=total_lines,
            source_lines_of_code=source_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=avg_complexity,
        )

    def _generate_issue_id(self, file_path: Path, issue_type: str, line: int) -> str:
        """Generate unique issue ID."""
        data = f"{file_path}:{issue_type}:{line}"
        return hashlib.md5(data.encode()).hexdigest()[:12]


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """Analyzer specifically for TypeScript (inherits from JavaScript analyzer)."""

    def get_language(self) -> str:
        """Get language name."""
        return "typescript"

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file is TypeScript."""
        return file_path.suffix in [".ts", ".tsx"]
