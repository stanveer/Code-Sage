"""Python code analyzer using AST."""

import ast
import hashlib
from pathlib import Path
from typing import List, Optional, Set, Dict, Any
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit

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


class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python code."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize Python analyzer."""
        super().__init__(config)
        self.issues: List[Issue] = []

    def get_language(self) -> str:
        """Get language name."""
        return "python"

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file is Python."""
        return file_path.suffix in [".py", ".pyw"]

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """
        Analyze a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            FileAnalysis with issues and metrics
        """
        self.issues = []

        try:
            content = read_file(file_path)
            tree = ast.parse(content, filename=str(file_path))

            # Run various checks
            self._check_syntax(file_path, content)
            self._check_code_smells(file_path, tree, content)
            self._check_best_practices(file_path, tree, content)
            self._check_potential_bugs(file_path, tree, content)

            # Calculate metrics
            metrics = self._calculate_metrics(file_path, content, tree)

            return FileAnalysis(
                file_path=str(file_path),
                language="python",
                issues=self.issues,
                metrics=metrics,
                success=True,
            )

        except SyntaxError as e:
            # Syntax error found
            issue = Issue(
                id=self._generate_issue_id(file_path, "syntax", e.lineno or 1),
                title="Python Syntax Error",
                description=str(e.msg),
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.BUG,
                location=CodeLocation(
                    file_path=str(file_path),
                    line_start=e.lineno or 1,
                    line_end=e.lineno or 1,
                    column_start=e.offset,
                ),
                code_snippet=self.get_code_snippet(file_path, e.lineno or 1, e.lineno or 1),
                auto_fixable=False,
            )
            self.issues.append(issue)

            return FileAnalysis(
                file_path=str(file_path),
                language="python",
                issues=self.issues,
                success=True,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return FileAnalysis(
                file_path=str(file_path),
                language="python",
                success=False,
                error=str(e),
            )

    def _check_syntax(self, file_path: Path, content: str) -> None:
        """Check for syntax issues (already handled by AST parsing)."""
        pass

    def _check_code_smells(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """Check for code smells."""
        visitor = CodeSmellVisitor(file_path, self)
        visitor.visit(tree)

        # Check complexity using radon
        try:
            complexities = cc_visit(content)
            for item in complexities:
                if item.complexity > self.config.analysis.max_complexity:
                    self.issues.append(
                        Issue(
                            id=self._generate_issue_id(file_path, "complexity", item.lineno),
                            title=f"High Complexity: {item.name}",
                            description=f"Cyclomatic complexity of {item.complexity} exceeds threshold of {self.config.analysis.max_complexity}",
                            severity=IssueSeverity.MEDIUM,
                            category=IssueCategory.COMPLEXITY,
                            location=CodeLocation(
                                file_path=str(file_path),
                                line_start=item.lineno,
                                line_end=item.endline,
                            ),
                            code_snippet=self.get_code_snippet(file_path, item.lineno, item.endline),
                            suggested_fix="Consider breaking this function into smaller, more focused functions.",
                            auto_fixable=False,
                        )
                    )
        except Exception as e:
            self.logger.debug(f"Could not calculate complexity: {e}")

    def _check_best_practices(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """Check for best practice violations."""
        visitor = BestPracticeVisitor(file_path, self)
        visitor.visit(tree)

    def _check_potential_bugs(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """Check for potential bugs."""
        visitor = BugDetectorVisitor(file_path, self)
        visitor.visit(tree)

    def _calculate_metrics(self, file_path: Path, content: str, tree: ast.AST) -> CodeMetrics:
        """Calculate code metrics."""
        lines = content.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())

        # Count comment lines
        comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                comment_lines += 1

        source_lines = total_lines - blank_lines - comment_lines

        # Calculate complexity metrics
        try:
            complexities = cc_visit(content)
            avg_complexity = (
                sum(c.complexity for c in complexities) / len(complexities)
                if complexities
                else 0
            )

            # Maintainability index
            mi_score = mi_visit(content, multi=True)
            mi_value = mi_score if isinstance(mi_score, (int, float)) else 0

            # Halstead metrics
            halstead = h_visit(content)
            h_difficulty = halstead.total.difficulty if halstead else 0
            h_effort = halstead.total.effort if halstead else 0

        except Exception:
            avg_complexity = 0
            mi_value = 0
            h_difficulty = 0
            h_effort = 0

        return CodeMetrics(
            lines_of_code=total_lines,
            source_lines_of_code=source_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=avg_complexity,
            maintainability_index=mi_value,
            halstead_difficulty=h_difficulty,
            halstead_effort=h_effort,
        )

    def _generate_issue_id(self, file_path: Path, issue_type: str, line: int) -> str:
        """Generate unique issue ID."""
        data = f"{file_path}:{issue_type}:{line}"
        return hashlib.md5(data.encode()).hexdigest()[:12]


class CodeSmellVisitor(ast.NodeVisitor):
    """AST visitor for detecting code smells."""

    def __init__(self, file_path: Path, analyzer: PythonAnalyzer):
        """Initialize visitor."""
        self.file_path = file_path
        self.analyzer = analyzer

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        # Check function length
        func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        max_length = self.analyzer.config.analysis.max_function_length

        if func_lines > max_length:
            self.analyzer.issues.append(
                Issue(
                    id=self.analyzer._generate_issue_id(self.file_path, "long_func", node.lineno),
                    title=f"Long Function: {node.name}",
                    description=f"Function has {func_lines} lines, exceeding the recommended {max_length} lines",
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.CODE_SMELL,
                    location=CodeLocation(
                        file_path=str(self.file_path),
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                    ),
                    code_snippet=self.analyzer.get_code_snippet(
                        self.file_path, node.lineno, node.end_lineno or node.lineno
                    ),
                    suggested_fix="Consider breaking this function into smaller, more focused functions.",
                    auto_fixable=False,
                )
            )

        # Check parameter count
        param_count = len(node.args.args)
        if param_count > 5:
            self.analyzer.issues.append(
                Issue(
                    id=self.analyzer._generate_issue_id(self.file_path, "many_params", node.lineno),
                    title=f"Too Many Parameters: {node.name}",
                    description=f"Function has {param_count} parameters. Consider using a configuration object.",
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.CODE_SMELL,
                    location=CodeLocation(
                        file_path=str(self.file_path),
                        line_start=node.lineno,
                        line_end=node.lineno,
                    ),
                    auto_fixable=False,
                )
            )

        self.generic_visit(node)


class BestPracticeVisitor(ast.NodeVisitor):
    """AST visitor for checking best practices."""

    def __init__(self, file_path: Path, analyzer: PythonAnalyzer):
        """Initialize visitor."""
        self.file_path = file_path
        self.analyzer = analyzer

    def visit_Try(self, node: ast.Try) -> None:
        """Check exception handling."""
        for handler in node.handlers:
            # Bare except clause
            if handler.type is None:
                self.analyzer.issues.append(
                    Issue(
                        id=self.analyzer._generate_issue_id(
                            self.file_path, "bare_except", handler.lineno
                        ),
                        title="Bare Except Clause",
                        description="Using bare 'except:' is discouraged. Catch specific exceptions instead.",
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.BEST_PRACTICE,
                        location=CodeLocation(
                            file_path=str(self.file_path),
                            line_start=handler.lineno,
                            line_end=handler.end_lineno or handler.lineno,
                        ),
                        code_snippet=self.analyzer.get_code_snippet(
                            self.file_path, handler.lineno, handler.end_lineno or handler.lineno
                        ),
                        suggested_fix="Replace with 'except Exception:' or catch specific exceptions",
                        auto_fixable=True,
                    )
                )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check imports."""
        # Check for wildcard imports (handled in ImportFrom)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from imports."""
        # Check for wildcard imports
        for alias in node.names:
            if alias.name == "*":
                self.analyzer.issues.append(
                    Issue(
                        id=self.analyzer._generate_issue_id(
                            self.file_path, "wildcard_import", node.lineno
                        ),
                        title="Wildcard Import",
                        description=f"Avoid wildcard imports from {node.module}. Import specific names instead.",
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.BEST_PRACTICE,
                        location=CodeLocation(
                            file_path=str(self.file_path),
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                        ),
                        auto_fixable=False,
                    )
                )

        self.generic_visit(node)


class BugDetectorVisitor(ast.NodeVisitor):
    """AST visitor for detecting potential bugs."""

    def __init__(self, file_path: Path, analyzer: PythonAnalyzer):
        """Initialize visitor."""
        self.file_path = file_path
        self.analyzer = analyzer
        self.defined_vars: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        # Check for mutable default arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.analyzer.issues.append(
                    Issue(
                        id=self.analyzer._generate_issue_id(
                            self.file_path, "mutable_default", node.lineno
                        ),
                        title=f"Mutable Default Argument: {node.name}",
                        description="Using mutable objects as default arguments can lead to unexpected behavior",
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.BUG,
                        location=CodeLocation(
                            file_path=str(self.file_path),
                            line_start=node.lineno,
                            line_end=node.lineno,
                        ),
                        code_snippet=self.analyzer.get_code_snippet(self.file_path, node.lineno, node.lineno),
                        suggested_fix="Use None as default and create the mutable object inside the function",
                        auto_fixable=True,
                    )
                )

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        """Visit comparison."""
        # Check for 'is' used with literals
        for i, op in enumerate(node.ops):
            if isinstance(op, (ast.Is, ast.IsNot)):
                comparator = node.comparators[i]
                if isinstance(comparator, (ast.Constant, ast.Num, ast.Str)):
                    if not (isinstance(comparator, ast.Constant) and comparator.value in (None, True, False)):
                        self.analyzer.issues.append(
                            Issue(
                                id=self.analyzer._generate_issue_id(
                                    self.file_path, "is_literal", node.lineno
                                ),
                                title="Identity Check with Literal",
                                description="Use '==' for value comparison, not 'is'",
                                severity=IssueSeverity.MEDIUM,
                                category=IssueCategory.BUG,
                                location=CodeLocation(
                                    file_path=str(self.file_path),
                                    line_start=node.lineno,
                                    line_end=node.end_lineno or node.lineno,
                                ),
                                suggested_fix="Replace 'is' with '=='",
                                auto_fixable=True,
                            )
                        )

        self.generic_visit(node)
