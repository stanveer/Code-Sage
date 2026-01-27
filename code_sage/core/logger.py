"""Structured logging system for Code Sage."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler


class CodeSageLogger:
    """Custom logger for Code Sage with rich output support."""

    def __init__(self, name: str, level: int = logging.INFO, log_file: Optional[Path] = None):
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Logging level
            log_file: Optional file path for log output
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        # Rich console handler for beautiful terminal output
        console = Console(stderr=True)
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        rich_handler.setLevel(level)
        self.logger.addHandler(rich_handler)

        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)

    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(message)

    def set_level(self, level: int) -> None:
        """Set logging level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# Global logger instance
_default_logger: Optional[CodeSageLogger] = None


def get_logger(
    name: str = "code_sage",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> CodeSageLogger:
    """
    Get or create logger instance.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path

    Returns:
        CodeSageLogger instance
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = CodeSageLogger(name, level, log_file)
    return _default_logger


def setup_logging(verbose: bool = False, debug: bool = False, log_file: Optional[Path] = None) -> CodeSageLogger:
    """
    Setup logging for the application.

    Args:
        verbose: Enable verbose output
        debug: Enable debug mode
        log_file: Optional log file path

    Returns:
        Configured logger
    """
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    
    if log_file is None and debug:
        log_dir = Path.cwd() / ".code-sage"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"code-sage-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    
    logger = get_logger(level=level, log_file=log_file)
    return logger
