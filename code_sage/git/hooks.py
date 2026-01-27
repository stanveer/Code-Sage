"""Git hooks integration for Code Sage."""

from pathlib import Path
from typing import Optional
import subprocess

from code_sage.core.logger import get_logger
from code_sage.core.config import Config


class GitHooksManager:
    """Manage Git hooks for Code Sage."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize hooks manager."""
        self.config = config or Config()
        self.logger = get_logger()

    def install_hooks(self, repo_path: Path) -> bool:
        """
        Install Git hooks.

        Args:
            repo_path: Path to Git repository

        Returns:
            True if successful
        """
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            self.logger.error(f"Not a Git repository: {repo_path}")
            return False

        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        # Install pre-commit hook
        if self.config.git.analyze_on_commit:
            self._install_pre_commit_hook(hooks_dir)

        self.logger.info("Git hooks installed successfully")
        return True

    def _install_pre_commit_hook(self, hooks_dir: Path) -> None:
        """Install pre-commit hook."""
        hook_path = hooks_dir / "pre-commit"
        
        hook_content = """#!/bin/sh
# Code Sage pre-commit hook

echo "Running Code Sage analysis..."
code-sage analyze . --severity critical

if [ $? -ne 0 ]; then
    echo "Critical issues found. Commit blocked."
    echo "Run 'code-sage analyze .' to see details."
    exit 1
fi

echo "Code analysis passed!"
exit 0
"""
        
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        
        self.logger.info(f"Pre-commit hook installed: {hook_path}")
