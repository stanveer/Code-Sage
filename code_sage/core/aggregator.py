"""Issue aggregation and ranking system."""

from typing import List, Dict, Optional
from collections import defaultdict
import difflib

from code_sage.core.models import Issue, IssueSeverity, IssueCategory, AnalysisResult


class IssueAggregator:
    """Aggregate and rank issues."""

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize aggregator.

        Args:
            similarity_threshold: Threshold for considering issues as duplicates
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
        """
        Remove duplicate issues.

        Args:
            issues: List of issues

        Returns:
            Deduplicated list of issues
        """
        unique_issues = []
        seen_signatures = set()

        for issue in issues:
            signature = self._get_issue_signature(issue)
            if signature not in seen_signatures:
                unique_issues.append(issue)
                seen_signatures.add(signature)

        return unique_issues

    def find_similar_issues(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """
        Group similar issues together.

        Args:
            issues: List of issues

        Returns:
            Dictionary mapping issue IDs to lists of similar issues
        """
        similar_groups: Dict[str, List[Issue]] = defaultdict(list)
        processed = set()

        for i, issue1 in enumerate(issues):
            if issue1.id in processed:
                continue

            group = [issue1]
            processed.add(issue1.id)

            for issue2 in issues[i + 1 :]:
                if issue2.id in processed:
                    continue

                if self._are_similar(issue1, issue2):
                    group.append(issue2)
                    processed.add(issue2.id)

            if len(group) > 1:
                similar_groups[issue1.id] = group

        return similar_groups

    def rank_issues(self, issues: List[Issue]) -> List[Issue]:
        """
        Rank issues by priority.

        Priority is calculated based on:
        - Severity
        - Category
        - Confidence
        - Auto-fixable

        Args:
            issues: List of issues

        Returns:
            Sorted list of issues by priority (highest first)
        """
        severity_weights = {
            IssueSeverity.CRITICAL: 100,
            IssueSeverity.HIGH: 75,
            IssueSeverity.MEDIUM: 50,
            IssueSeverity.LOW: 25,
            IssueSeverity.INFO: 10,
        }

        category_weights = {
            IssueCategory.SECURITY: 20,
            IssueCategory.BUG: 15,
            IssueCategory.TYPE_ERROR: 10,
            IssueCategory.PERFORMANCE: 8,
            IssueCategory.BEST_PRACTICE: 5,
            IssueCategory.CODE_SMELL: 3,
            IssueCategory.STYLE: 1,
            IssueCategory.DUPLICATION: 2,
            IssueCategory.COMPLEXITY: 4,
            IssueCategory.MAINTAINABILITY: 3,
        }

        def calculate_priority(issue: Issue) -> float:
            priority = severity_weights.get(issue.severity, 0)
            priority += category_weights.get(issue.category, 0)
            priority *= issue.confidence
            if issue.auto_fixable:
                priority += 5  # Bonus for auto-fixable issues
            return priority

        return sorted(issues, key=calculate_priority, reverse=True)

    def filter_issues(
        self,
        issues: List[Issue],
        min_severity: Optional[IssueSeverity] = None,
        categories: Optional[List[IssueCategory]] = None,
        auto_fixable_only: bool = False,
    ) -> List[Issue]:
        """
        Filter issues based on criteria.

        Args:
            issues: List of issues
            min_severity: Minimum severity level
            categories: List of categories to include
            auto_fixable_only: Only include auto-fixable issues

        Returns:
            Filtered list of issues
        """
        filtered = issues

        if min_severity:
            filtered = [i for i in filtered if i.severity >= min_severity]

        if categories:
            filtered = [i for i in filtered if i.category in categories]

        if auto_fixable_only:
            filtered = [i for i in filtered if i.auto_fixable]

        return filtered

    def generate_summary(self, result: AnalysisResult) -> Dict[str, any]:
        """
        Generate a summary of analysis results.

        Args:
            result: Analysis result

        Returns:
            Summary dictionary
        """
        issues = result.get_all_issues()

        summary = {
            "total_issues": len(issues),
            "by_severity": result.get_severity_counts(),
            "by_category": result.get_category_counts(),
            "by_file": self._count_issues_by_file(result),
            "auto_fixable": sum(1 for i in issues if i.auto_fixable),
            "high_priority": sum(1 for i in issues if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]),
            "files_with_issues": len([fa for fa in result.file_analyses if fa.issues]),
            "files_without_issues": len([fa for fa in result.file_analyses if not fa.issues]),
        }

        return summary

    def _get_issue_signature(self, issue: Issue) -> str:
        """Get unique signature for an issue."""
        return f"{issue.location.file_path}:{issue.location.line_start}:{issue.title}:{issue.category.value}"

    def _are_similar(self, issue1: Issue, issue2: Issue) -> bool:
        """Check if two issues are similar."""
        # Same category and severity
        if issue1.category != issue2.category or issue1.severity != issue2.severity:
            return False

        # Similar titles
        title_similarity = difflib.SequenceMatcher(None, issue1.title, issue2.title).ratio()
        if title_similarity < self.similarity_threshold:
            return False

        # Similar descriptions
        desc_similarity = difflib.SequenceMatcher(
            None, issue1.description, issue2.description
        ).ratio()
        if desc_similarity < self.similarity_threshold:
            return False

        return True

    def _count_issues_by_file(self, result: AnalysisResult) -> Dict[str, int]:
        """Count issues per file."""
        counts = {}
        for fa in result.file_analyses:
            if fa.issues:
                counts[fa.file_path] = len(fa.issues)
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
