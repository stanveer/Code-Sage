"""Main analysis engine for Code Sage."""

from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from code_sage.core.config import Config
from code_sage.core.models import AnalysisResult, FileAnalysis
from code_sage.core.analyzer import BaseAnalyzer, get_analyzer_registry
from code_sage.core.aggregator import IssueAggregator
from code_sage.core.pattern_matcher import PatternMatcher
from code_sage.core.logger import get_logger
from code_sage.utils.file_utils import FileDiscovery, read_file


class AnalysisEngine:
    """Main engine for code analysis."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize analysis engine.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.logger = get_logger()
        self.registry = get_analyzer_registry()
        self.aggregator = IssueAggregator()
        self.pattern_matcher = PatternMatcher()
        
        # Register default analyzers
        self._register_default_analyzers()

    def _register_default_analyzers(self) -> None:
        """Register default language analyzers."""
        from code_sage.analyzers.python_analyzer import PythonAnalyzer
        from code_sage.analyzers.javascript_analyzer import JavaScriptAnalyzer, TypeScriptAnalyzer

        self.registry.register(PythonAnalyzer(self.config))
        self.registry.register(JavaScriptAnalyzer(self.config))
        self.registry.register(TypeScriptAnalyzer(self.config))

    def analyze_path(self, path: Path) -> AnalysisResult:
        """
        Analyze a file or directory.

        Args:
            path: Path to file or directory

        Returns:
            AnalysisResult with findings
        """
        start_time = time.time()
        result = AnalysisResult(project_path=str(path))

        # Discover files to analyze
        discovery = FileDiscovery(
            include_patterns=self.config.include_patterns,
            ignore_patterns=self.config.ignore_patterns,
            respect_gitignore=True,
        )

        files = discovery.discover_files(path, recursive=True)
        self.logger.info(f"Found {len(files)} files to analyze")

        # Analyze files
        if self.config.analysis.parallel_analysis and len(files) > 1:
            file_analyses = self._analyze_parallel(files)
        else:
            file_analyses = self._analyze_sequential(files)

        # Add results
        for file_analysis in file_analyses:
            result.add_file_analysis(file_analysis)

        # Deduplicate and rank issues
        all_issues = result.get_all_issues()
        unique_issues = self.aggregator.deduplicate_issues(all_issues)
        ranked_issues = self.aggregator.rank_issues(unique_issues)

        # Update file analyses with ranked issues
        self._update_file_analyses_with_ranked_issues(result, ranked_issues)

        # Generate summary
        result.total_time = time.time() - start_time
        result.generate_summary()

        self.logger.info(f"Analysis completed in {result.total_time:.2f}s")
        self.logger.info(f"Found {result.total_issues} issues across {result.total_files} files")

        return result

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """
        Analyze a single file.

        Args:
            file_path: Path to file

        Returns:
            FileAnalysis with findings
        """
        analyzer = self.registry.get_analyzer(file_path)
        if not analyzer:
            self.logger.warning(f"No analyzer found for {file_path}")
            return FileAnalysis(
                file_path=str(file_path),
                language="unknown",
                success=False,
                error="No analyzer available for this file type",
            )

        # Analyze with the appropriate analyzer
        file_analysis = analyzer.analyze_with_timing(file_path)

        # Also run pattern matching
        try:
            content = read_file(file_path)
            pattern_issues = self.pattern_matcher.match_file(
                file_path, content, file_analysis.language
            )
            file_analysis.issues.extend(pattern_issues)
        except Exception as e:
            self.logger.warning(f"Pattern matching failed for {file_path}: {e}")

        return file_analysis

    def _analyze_sequential(self, files: List[Path]) -> List[FileAnalysis]:
        """Analyze files sequentially."""
        results = []
        for i, file_path in enumerate(files, 1):
            self.logger.info(f"Analyzing {i}/{len(files)}: {file_path.name}")
            result = self.analyze_file(file_path)
            results.append(result)
        return results

    def _analyze_parallel(self, files: List[Path]) -> List[FileAnalysis]:
        """Analyze files in parallel."""
        results = []
        max_workers = min(self.config.analysis.max_workers, len(files))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_file, file_path): file_path for file_path in files
            }

            for i, future in enumerate(as_completed(future_to_file), 1):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.info(f"Completed {i}/{len(files)}: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Error analyzing {file_path}: {e}")
                    results.append(
                        FileAnalysis(
                            file_path=str(file_path),
                            language="unknown",
                            success=False,
                            error=str(e),
                        )
                    )

        return results

    def _update_file_analyses_with_ranked_issues(
        self, result: AnalysisResult, ranked_issues: List
    ) -> None:
        """Update file analyses with ranked and deduplicated issues."""
        # Group issues by file
        issues_by_file = {}
        for issue in ranked_issues:
            file_path = issue.location.file_path
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        # Update file analyses
        for file_analysis in result.file_analyses:
            file_analysis.issues = issues_by_file.get(file_analysis.file_path, [])
