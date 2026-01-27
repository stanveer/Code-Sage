"""
Code Sage - AI-powered code analyzer.

An intelligent code analysis assistant that autonomously scans your codebase,
identifies errors, detects code smells, finds security vulnerabilities, and
suggests or automatically applies fixes.
"""

__version__ = "1.0.0"
__author__ = "Code Sage Team"
__license__ = "MIT"

from code_sage.core.models import Issue, IssueSeverity, IssueCategory, AnalysisResult

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Issue",
    "IssueSeverity",
    "IssueCategory",
    "AnalysisResult",
]
