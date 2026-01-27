"""Tests for Python analyzer."""

import pytest
from pathlib import Path
import tempfile

from code_sage.analyzers.python_analyzer import PythonAnalyzer
from code_sage.core.config import Config
from code_sage.core.models import IssueSeverity, IssueCategory


class TestPythonAnalyzer:
    """Test Python analyzer."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.analyzer = PythonAnalyzer(Config())

    def test_can_analyze(self) -> None:
        """Test file type detection."""
        assert self.analyzer.can_analyze(Path("test.py"))
        assert self.analyzer.can_analyze(Path("test.pyw"))
        assert not self.analyzer.can_analyze(Path("test.js"))

    def test_syntax_error_detection(self) -> None:
        """Test syntax error detection."""
        code = """
def broken_function(
    print("Missing closing parenthesis")
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            
            result = self.analyzer.analyze_file(Path(f.name))
            
            assert result.success
            assert len(result.issues) > 0
            assert any(issue.severity == IssueSeverity.CRITICAL for issue in result.issues)

    def test_mutable_default_detection(self) -> None:
        """Test mutable default argument detection."""
        code = """
def function_with_mutable_default(items=[]):
    items.append(1)
    return items
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            
            result = self.analyzer.analyze_file(Path(f.name))
            
            # Should detect mutable default argument
            mutable_default_issues = [
                issue for issue in result.issues
                if "Mutable Default" in issue.title
            ]
            assert len(mutable_default_issues) > 0

    def test_bare_except_detection(self) -> None:
        """Test bare except clause detection."""
        code = """
try:
    risky_operation()
except:
    pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            
            result = self.analyzer.analyze_file(Path(f.name))
            
            bare_except_issues = [
                issue for issue in result.issues
                if "Bare Except" in issue.title
            ]
            assert len(bare_except_issues) > 0

    def test_metrics_calculation(self) -> None:
        """Test code metrics calculation."""
        code = """
# This is a comment
def simple_function():
    '''Docstring'''
    return 42

def another_function():
    pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            
            result = self.analyzer.analyze_file(Path(f.name))
            
            assert result.metrics is not None
            assert result.metrics.lines_of_code > 0
            assert result.metrics.source_lines_of_code > 0

    def test_complexity_detection(self) -> None:
        """Test complexity detection."""
        # Create a complex function
        code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        return "very high"
                    return "high"
                return "medium-high"
            return "medium"
        return "low"
    return "negative"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            
            result = self.analyzer.analyze_file(Path(f.name))
            
            # Should detect high complexity
            complexity_issues = [
                issue for issue in result.issues
                if issue.category == IssueCategory.COMPLEXITY
            ]
            assert len(complexity_issues) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
