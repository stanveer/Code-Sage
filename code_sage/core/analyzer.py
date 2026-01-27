"""Base analyzer interface for Code Sage."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import time

from code_sage.core.models import Issue, FileAnalysis, CodeMetrics
from code_sage.core.config import Config
from code_sage.core.logger import get_logger
from code_sage.utils.file_utils import read_file


class BaseAnalyzer(ABC):
    """Abstract base class for all language analyzers."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize analyzer.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.logger = get_logger()
        self.language = self.get_language()

    @abstractmethod
    def get_language(self) -> str:
        """
        Get the language this analyzer supports.

        Returns:
            Language name (e.g., 'python', 'javascript')
        """
        pass

    @abstractmethod
    def can_analyze(self, file_path: Path) -> bool:
        """
        Check if this analyzer can analyze the given file.

        Args:
            file_path: Path to file

        Returns:
            True if analyzer supports this file
        """
        pass

    @abstractmethod
    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """
        Analyze a single file.

        Args:
            file_path: Path to file to analyze

        Returns:
            FileAnalysis object containing results
        """
        pass

    def analyze_with_timing(self, file_path: Path) -> FileAnalysis:
        """
        Analyze file with timing information.

        Args:
            file_path: Path to file

        Returns:
            FileAnalysis with timing data
        """
        start_time = time.time()
        
        try:
            result = self.analyze_file(file_path)
            result.analysis_time = time.time() - start_time
            return result
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return FileAnalysis(
                file_path=str(file_path),
                language=self.language,
                success=False,
                error=str(e),
                analysis_time=time.time() - start_time,
            )

    def get_code_snippet(self, file_path: Path, line_start: int, line_end: int, context: int = 2) -> str:
        """
        Get code snippet with context.

        Args:
            file_path: Path to file
            line_start: Starting line number
            line_end: Ending line number
            context: Number of context lines before and after

        Returns:
            Code snippet as string
        """
        try:
            content = read_file(file_path)
            lines = content.splitlines()
            
            # Calculate bounds with context
            start = max(0, line_start - 1 - context)
            end = min(len(lines), line_end + context)
            
            snippet_lines = []
            for i in range(start, end):
                prefix = "→ " if line_start - 1 <= i < line_end else "  "
                snippet_lines.append(f"{prefix}{i + 1:4d} | {lines[i]}")
            
            return "\n".join(snippet_lines)
        except Exception as e:
            self.logger.warning(f"Failed to get code snippet: {e}")
            return ""

    def calculate_basic_metrics(self, file_path: Path) -> CodeMetrics:
        """
        Calculate basic code metrics.

        Args:
            file_path: Path to file

        Returns:
            CodeMetrics object
        """
        try:
            content = read_file(file_path)
            lines = content.splitlines()
            
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            
            # Simple comment detection
            comment_lines = 0
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(("#", "//", "--", "/*", "*", "*/")):
                    comment_lines += 1
            
            source_lines = total_lines - blank_lines - comment_lines
            
            return CodeMetrics(
                lines_of_code=total_lines,
                source_lines_of_code=source_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
            )
        except Exception as e:
            self.logger.warning(f"Failed to calculate metrics: {e}")
            return CodeMetrics()

    def should_analyze_category(self, category: str) -> bool:
        """
        Check if a category should be analyzed based on config.

        Args:
            category: Issue category

        Returns:
            True if category should be analyzed
        """
        return category in self.config.analysis.enabled_categories

    def should_report_issue(self, severity: str) -> bool:
        """
        Check if an issue should be reported based on severity threshold.

        Args:
            severity: Issue severity

        Returns:
            True if issue should be reported
        """
        severity_levels = ["info", "low", "medium", "high", "critical"]
        min_level = self.config.analysis.min_severity
        
        try:
            return severity_levels.index(severity) >= severity_levels.index(min_level)
        except ValueError:
            return True


class AnalyzerRegistry:
    """Registry for managing analyzers."""

    def __init__(self) -> None:
        """Initialize analyzer registry."""
        self._analyzers: List[BaseAnalyzer] = []

    def register(self, analyzer: BaseAnalyzer) -> None:
        """
        Register an analyzer.

        Args:
            analyzer: Analyzer instance to register
        """
        self._analyzers.append(analyzer)

    def get_analyzer(self, file_path: Path) -> Optional[BaseAnalyzer]:
        """
        Get appropriate analyzer for a file.

        Args:
            file_path: Path to file

        Returns:
            Analyzer instance or None if no suitable analyzer found
        """
        for analyzer in self._analyzers:
            if analyzer.can_analyze(file_path):
                return analyzer
        return None

    def get_all_analyzers(self) -> List[BaseAnalyzer]:
        """
        Get all registered analyzers.

        Returns:
            List of analyzer instances
        """
        return self._analyzers.copy()

    def get_supported_languages(self) -> List[str]:
        """
        Get all supported languages.

        Returns:
            List of language names
        """
        return [analyzer.get_language() for analyzer in self._analyzers]


# Global analyzer registry
_registry = AnalyzerRegistry()


def get_analyzer_registry() -> AnalyzerRegistry:
    """
    Get the global analyzer registry.

    Returns:
        AnalyzerRegistry instance
    """
    return _registry
