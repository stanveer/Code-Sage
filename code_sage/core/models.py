"""Core data models for Code Sage."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class IssueSeverity(Enum):
    """Severity levels for issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    def __lt__(self, other: "IssueSeverity") -> bool:
        """Allow severity comparison."""
        severity_order = [
            IssueSeverity.INFO,
            IssueSeverity.LOW,
            IssueSeverity.MEDIUM,
            IssueSeverity.HIGH,
            IssueSeverity.CRITICAL,
        ]
        return severity_order.index(self) < severity_order.index(other)


class IssueCategory(Enum):
    """Categories of issues."""

    SECURITY = "security"
    BUG = "bug"
    CODE_SMELL = "code_smell"
    TYPE_ERROR = "type_error"
    STYLE = "style"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"
    DUPLICATION = "duplication"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"


@dataclass
class CodeLocation:
    """Location of code in a file."""

    file_path: str
    line_start: int
    line_end: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None

    def __str__(self) -> str:
        """String representation of location."""
        if self.line_start == self.line_end:
            return f"{self.file_path}:{self.line_start}"
        return f"{self.file_path}:{self.line_start}-{self.line_end}"


@dataclass
class Issue:
    """Represents a code issue found during analysis."""

    id: str
    title: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    location: CodeLocation
    code_snippet: Optional[str] = None
    suggested_fix: Optional[str] = None
    fix_description: Optional[str] = None
    ai_explanation: Optional[str] = None
    confidence: float = 1.0
    auto_fixable: bool = False
    rule_id: Optional[str] = None
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category.value,
            "location": {
                "file": self.location.file_path,
                "line_start": self.location.line_start,
                "line_end": self.location.line_end,
                "column_start": self.location.column_start,
                "column_end": self.location.column_end,
            },
            "code_snippet": self.code_snippet,
            "suggested_fix": self.suggested_fix,
            "fix_description": self.fix_description,
            "ai_explanation": self.ai_explanation,
            "confidence": self.confidence,
            "auto_fixable": self.auto_fixable,
            "rule_id": self.rule_id,
            "references": self.references,
            "metadata": self.metadata,
        }


@dataclass
class CodeMetrics:
    """Code quality metrics."""

    lines_of_code: int = 0
    source_lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    cyclomatic_complexity: float = 0.0
    cognitive_complexity: float = 0.0
    maintainability_index: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "lines_of_code": self.lines_of_code,
            "source_lines_of_code": self.source_lines_of_code,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "cognitive_complexity": self.cognitive_complexity,
            "maintainability_index": self.maintainability_index,
            "halstead_difficulty": self.halstead_difficulty,
            "halstead_effort": self.halstead_effort,
        }


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file_path: str
    language: str
    issues: List[Issue] = field(default_factory=list)
    metrics: Optional[CodeMetrics] = None
    analysis_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[Issue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: IssueCategory) -> List[Issue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert file analysis to dictionary."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "analysis_time": self.analysis_time,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class AnalysisResult:
    """Complete analysis results for a project."""

    project_path: str
    timestamp: datetime = field(default_factory=datetime.now)
    file_analyses: List[FileAnalysis] = field(default_factory=list)
    total_files: int = 0
    total_issues: int = 0
    total_time: float = 0.0
    languages: Dict[str, int] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

    def add_file_analysis(self, file_analysis: FileAnalysis) -> None:
        """Add a file analysis result."""
        self.file_analyses.append(file_analysis)
        self.total_files += 1
        self.total_issues += len(file_analysis.issues)
        self.total_time += file_analysis.analysis_time

        # Update language statistics
        lang = file_analysis.language
        self.languages[lang] = self.languages.get(lang, 0) + 1

    def get_all_issues(self) -> List[Issue]:
        """Get all issues across all files."""
        issues = []
        for file_analysis in self.file_analyses:
            issues.extend(file_analysis.issues)
        return issues

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[Issue]:
        """Get all issues of a specific severity."""
        return [issue for issue in self.get_all_issues() if issue.severity == severity]

    def get_issues_by_category(self, category: IssueCategory) -> List[Issue]:
        """Get all issues of a specific category."""
        return [issue for issue in self.get_all_issues() if issue.category == category]

    def get_severity_counts(self) -> Dict[str, int]:
        """Get count of issues by severity."""
        counts = {severity.value: 0 for severity in IssueSeverity}
        for issue in self.get_all_issues():
            counts[issue.severity.value] += 1
        return counts

    def get_category_counts(self) -> Dict[str, int]:
        """Get count of issues by category."""
        counts = {category.value: 0 for category in IssueCategory}
        for issue in self.get_all_issues():
            counts[issue.category.value] += 1
        return counts

    def generate_summary(self) -> None:
        """Generate analysis summary."""
        self.summary = {
            "project_path": self.project_path,
            "timestamp": self.timestamp.isoformat(),
            "total_files": self.total_files,
            "total_issues": self.total_issues,
            "total_time": round(self.total_time, 2),
            "languages": self.languages,
            "severity_counts": self.get_severity_counts(),
            "category_counts": self.get_category_counts(),
            "auto_fixable_count": len([i for i in self.get_all_issues() if i.auto_fixable]),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            "project_path": self.project_path,
            "timestamp": self.timestamp.isoformat(),
            "file_analyses": [fa.to_dict() for fa in self.file_analyses],
            "total_files": self.total_files,
            "total_issues": self.total_issues,
            "total_time": self.total_time,
            "languages": self.languages,
            "summary": self.summary,
        }
