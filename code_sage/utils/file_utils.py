"""File system utilities for Code Sage."""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Set, Tuple
from code_sage.core.exceptions import FileAccessError


class FileDiscovery:
    """File discovery and filtering utility."""

    # Language extension mapping
    LANGUAGE_EXTENSIONS = {
        "python": [".py", ".pyw"],
        "javascript": [".js", ".jsx", ".mjs", ".cjs"],
        "typescript": [".ts", ".tsx"],
        "java": [".java"],
        "go": [".go"],
        "ruby": [".rb"],
        "php": [".php"],
        "rust": [".rs"],
        "c": [".c", ".h"],
        "cpp": [".cpp", ".hpp", ".cc", ".cxx", ".hxx", ".c++", ".h++"],
        "csharp": [".cs"],
        "swift": [".swift"],
        "kotlin": [".kt", ".kts"],
        "scala": [".scala"],
        "r": [".r", ".R"],
        "perl": [".pl", ".pm"],
        "lua": [".lua"],
        "shell": [".sh", ".bash", ".zsh"],
    }

    def __init__(
        self,
        include_patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        respect_gitignore: bool = True,
    ):
        """
        Initialize file discovery.

        Args:
            include_patterns: File patterns to include
            ignore_patterns: File patterns to ignore
            respect_gitignore: Whether to respect .gitignore files
        """
        self.include_patterns = include_patterns or ["*.py", "*.js", "*.ts", "*.java", "*.go"]
        self.ignore_patterns = ignore_patterns or []
        self.respect_gitignore = respect_gitignore
        self.gitignore_patterns: Set[str] = set()

    def discover_files(self, root_path: Path, recursive: bool = True) -> List[Path]:
        """
        Discover files to analyze.

        Args:
            root_path: Root directory to search
            recursive: Whether to search recursively

        Returns:
            List of file paths to analyze
        """
        if not root_path.exists():
            raise FileAccessError(f"Path does not exist", str(root_path))

        # If it's a file, return it directly
        if root_path.is_file():
            if self._should_include_file(root_path):
                return [root_path]
            return []

        # Load .gitignore patterns if needed
        if self.respect_gitignore:
            self._load_gitignore(root_path)

        # Discover files
        files = []
        if recursive:
            for file_path in root_path.rglob("*"):
                if file_path.is_file() and self._should_include_file(file_path):
                    files.append(file_path)
        else:
            for file_path in root_path.iterdir():
                if file_path.is_file() and self._should_include_file(file_path):
                    files.append(file_path)

        return sorted(files)

    def _should_include_file(self, file_path: Path) -> bool:
        """
        Check if a file should be included in analysis.

        Args:
            file_path: Path to check

        Returns:
            True if file should be included
        """
        # Check ignore patterns
        if self._is_ignored(file_path):
            return False

        # Check include patterns
        if self.include_patterns:
            return any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.include_patterns)

        return True

    def _is_ignored(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored
        """
        # Check explicit ignore patterns
        relative_path = str(file_path)
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True

        # Check gitignore patterns
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True

        # Ignore common patterns
        common_ignores = [
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            "venv",
            "env",
            ".env",
            "build",
            "dist",
            ".pytest_cache",
            ".tox",
            "*.pyc",
            "*.pyo",
            "*.so",
            "*.dylib",
            "*.min.js",
            "*.bundle.js",
        ]
        
        for ignore in common_ignores:
            if ignore in str(file_path):
                return True

        return False

    def _load_gitignore(self, root_path: Path) -> None:
        """
        Load .gitignore patterns.

        Args:
            root_path: Root directory to search for .gitignore
        """
        gitignore_path = root_path / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            self.gitignore_patterns.add(line)
            except Exception:
                pass  # Ignore errors reading .gitignore

    @staticmethod
    def detect_language(file_path: Path) -> Optional[str]:
        """
        Detect language from file extension.

        Args:
            file_path: Path to file

        Returns:
            Language name or None if unknown
        """
        ext = file_path.suffix.lower()
        for language, extensions in FileDiscovery.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return language
        return None

    @staticmethod
    def get_supported_languages() -> List[str]:
        """
        Get list of supported languages.

        Returns:
            List of language names
        """
        return list(FileDiscovery.LANGUAGE_EXTENSIONS.keys())


def read_file(file_path: Path, encoding: str = "utf-8") -> str:
    """
    Read file contents safely.

    Args:
        file_path: Path to file
        encoding: File encoding

    Returns:
        File contents as string

    Raises:
        FileAccessError: If file cannot be read
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            raise FileAccessError(f"Cannot read file: {e}", str(file_path))
    except Exception as e:
        raise FileAccessError(f"Cannot read file: {e}", str(file_path))


def write_file(file_path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write content to file safely.

    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding

    Raises:
        FileAccessError: If file cannot be written
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise FileAccessError(f"Cannot write file: {e}", str(file_path))


def ensure_directory(directory: Path) -> None:
    """
    Ensure directory exists.

    Args:
        directory: Directory path

    Raises:
        FileAccessError: If directory cannot be created
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileAccessError(f"Cannot create directory: {e}", str(directory))


def get_file_lines(file_path: Path, start: int = 1, end: Optional[int] = None) -> List[str]:
    """
    Get specific lines from a file.

    Args:
        file_path: Path to file
        start: Starting line number (1-indexed)
        end: Ending line number (inclusive, None for all)

    Returns:
        List of lines

    Raises:
        FileAccessError: If file cannot be read
    """
    content = read_file(file_path)
    lines = content.splitlines()
    
    if end is None:
        return lines[start - 1 :]
    return lines[start - 1 : end]


def count_lines(file_path: Path) -> Tuple[int, int, int]:
    """
    Count lines in a file.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (total lines, source lines, comment lines)

    Raises:
        FileAccessError: If file cannot be read
    """
    content = read_file(file_path)
    lines = content.splitlines()
    
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    
    # Simple comment detection (works for most languages)
    comment_lines = 0
    in_block_comment = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Block comment detection
        if "/*" in stripped or "'''":
            in_block_comment = True
        if "*/" in stripped or "'''":
            in_block_comment = False
            comment_lines += 1
            continue
            
        if in_block_comment:
            comment_lines += 1
        elif stripped.startswith(("#", "//", "--")):
            comment_lines += 1
    
    source_lines = total_lines - blank_lines - comment_lines
    
    return total_lines, source_lines, comment_lines
