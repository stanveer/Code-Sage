"""AI-powered issue enrichment."""

from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from code_sage.core.models import Issue, FileAnalysis
from code_sage.core.config import Config
from code_sage.ai.provider import get_ai_provider
from code_sage.core.logger import get_logger
from code_sage.utils.file_utils import read_file
from pathlib import Path


class AIEnrichment:
    """Enrich issues with AI-powered explanations and fixes."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize AI enrichment.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.logger = get_logger()
        self.provider = get_ai_provider(self.config.ai)

    def enrich_issues(self, issues: List[Issue], max_issues: int = 10) -> List[Issue]:
        """
        Enrich issues with AI explanations.

        Args:
            issues: List of issues to enrich
            max_issues: Maximum number of issues to enrich (for API cost control)

        Returns:
            Enriched issues
        """
        if not self.provider:
            self.logger.info("AI provider not enabled, skipping enrichment")
            return issues

        # Prioritize critical/high severity issues
        sorted_issues = sorted(
            issues, key=lambda x: (x.severity.value, x.category.value), reverse=True
        )
        
        issues_to_enrich = sorted_issues[:max_issues]
        enriched = []

        self.logger.info(f"Enriching {len(issues_to_enrich)} issues with AI")

        for issue in issues_to_enrich:
            try:
                # Get AI explanation
                if not issue.ai_explanation:
                    issue.ai_explanation = self.provider.explain_issue(
                        issue_description=issue.description,
                        code=issue.code_snippet or "",
                        language=self._infer_language(issue),
                    )

                # Get AI fix suggestion
                if not issue.suggested_fix and issue.severity.value in ["critical", "high", "medium"]:
                    fix_result = self.provider.suggest_fix(
                        issue_description=issue.description,
                        code=issue.code_snippet or "",
                        language=self._infer_language(issue),
                    )
                    issue.suggested_fix = fix_result.get("fixed_code", "")
                    issue.fix_description = fix_result.get("explanation", "")

                enriched.append(issue)
                self.logger.debug(f"Enriched issue: {issue.title}")

            except Exception as e:
                self.logger.warning(f"Failed to enrich issue {issue.id}: {e}")
                enriched.append(issue)

        # Add remaining issues without enrichment
        enriched.extend(sorted_issues[max_issues:])

        return enriched

    def enrich_file_analysis(self, file_analysis: FileAnalysis) -> FileAnalysis:
        """
        Enrich a file analysis with AI.

        Args:
            file_analysis: File analysis to enrich

        Returns:
            Enriched file analysis
        """
        if not self.provider or not file_analysis.issues:
            return file_analysis

        file_analysis.issues = self.enrich_issues(file_analysis.issues)
        return file_analysis

    def _infer_language(self, issue: Issue) -> str:
        """Infer language from file path."""
        file_path = Path(issue.location.file_path)
        ext = file_path.suffix.lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
        }

        return language_map.get(ext, "unknown")
