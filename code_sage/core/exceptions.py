"""Custom exceptions for Code Sage."""


class CodeSageError(Exception):
    """Base exception for all Code Sage errors."""

    pass


class ConfigurationError(CodeSageError):
    """Raised when there's a configuration error."""

    pass


class AnalysisError(CodeSageError):
    """Raised when analysis fails."""

    def __init__(self, message: str, file_path: str = None, line: int = None):
        """
        Initialize analysis error.

        Args:
            message: Error message
            file_path: Optional file path where error occurred
            line: Optional line number where error occurred
        """
        self.file_path = file_path
        self.line = line
        super().__init__(message)

    def __str__(self) -> str:
        """String representation of error."""
        if self.file_path and self.line:
            return f"{self.file_path}:{self.line}: {super().__str__()}"
        elif self.file_path:
            return f"{self.file_path}: {super().__str__()}"
        return super().__str__()


class ParserError(AnalysisError):
    """Raised when code parsing fails."""

    pass


class LanguageNotSupportedError(CodeSageError):
    """Raised when attempting to analyze unsupported language."""

    def __init__(self, language: str):
        """
        Initialize language not supported error.

        Args:
            language: The unsupported language
        """
        self.language = language
        super().__init__(f"Language not supported: {language}")


class AIProviderError(CodeSageError):
    """Raised when AI provider encounters an error."""

    pass


class SecurityScanError(CodeSageError):
    """Raised when security scanning fails."""

    pass


class GitOperationError(CodeSageError):
    """Raised when git operations fail."""

    pass


class ReportGenerationError(CodeSageError):
    """Raised when report generation fails."""

    pass


class FileAccessError(CodeSageError):
    """Raised when file access fails."""

    def __init__(self, message: str, file_path: str):
        """
        Initialize file access error.

        Args:
            message: Error message
            file_path: Path to the file
        """
        self.file_path = file_path
        super().__init__(f"{file_path}: {message}")


class CacheError(CodeSageError):
    """Raised when cache operations fail."""

    pass


class ValidationError(CodeSageError):
    """Raised when validation fails."""

    pass
