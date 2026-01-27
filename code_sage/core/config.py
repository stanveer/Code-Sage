"""Configuration management for Code Sage."""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class AIConfig:
    """AI provider configuration."""

    provider: str = "openai"  # openai, anthropic, or both
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-opus-20240229"
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 30
    enabled: bool = False  # AI is opt-in, not opt-out


@dataclass
class AnalysisConfig:
    """Analysis configuration."""

    enabled_languages: List[str] = field(
        default_factory=lambda: ["python", "javascript", "typescript", "java", "go"]
    )
    enabled_categories: List[str] = field(
        default_factory=lambda: [
            "security",
            "bug",
            "code_smell",
            "type_error",
            "performance",
            "best_practice",
        ]
    )
    min_severity: str = "info"
    max_complexity: int = 15
    max_function_length: int = 50
    enable_type_checking: bool = True
    enable_security_scan: bool = True
    enable_metrics: bool = True
    parallel_analysis: bool = True
    max_workers: int = 4


@dataclass
class SecurityConfig:
    """Security scanning configuration."""

    enable_secrets_scan: bool = True
    enable_dependency_scan: bool = True
    enable_owasp_scan: bool = True
    check_cve_database: bool = True
    min_entropy_threshold: float = 4.5
    secret_patterns: List[str] = field(default_factory=list)


@dataclass
class OutputConfig:
    """Output and reporting configuration."""

    format: str = "rich"  # rich, json, sarif, junit
    output_dir: str = "./reports"
    generate_html: bool = True
    generate_pdf: bool = False
    generate_json: bool = True
    show_code_snippets: bool = True
    show_ai_explanations: bool = True
    verbose: bool = False


@dataclass
class GitConfig:
    """Git integration configuration."""

    enable_hooks: bool = False
    enable_pr_analysis: bool = False
    analyze_on_commit: bool = False
    analyze_on_push: bool = False
    block_on_critical: bool = True
    github_token: Optional[str] = None


@dataclass
class CacheConfig:
    """Caching configuration."""

    enabled: bool = True
    cache_dir: str = "./.code-sage-cache"
    ttl_seconds: int = 3600
    max_size_mb: int = 500


@dataclass
class Config:
    """Main configuration class for Code Sage."""

    ai: AIConfig = field(default_factory=AIConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    git: GitConfig = field(default_factory=GitConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Ignore patterns
    ignore_patterns: List[str] = field(
        default_factory=lambda: [
            "node_modules/*",
            "venv/*",
            "env/*",
            ".git/*",
            "*.min.js",
            "*.bundle.js",
            "build/*",
            "dist/*",
            "*.pyc",
            "__pycache__/*",
        ]
    )

    # File patterns to include
    include_patterns: List[str] = field(
        default_factory=lambda: [
            "*.py",
            "*.js",
            "*.ts",
            "*.jsx",
            "*.tsx",
            "*.java",
            "*.go",
            "*.rb",
            "*.php",
            "*.rs",
            "*.c",
            "*.cpp",
            "*.h",
            "*.hpp",
        ]
    )

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from a file (YAML or JSON)."""
        if not config_path.exists():
            return cls()

        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif config_path.suffix == ".json":
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        return cls.from_dict(data or {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        config = cls()

        if "ai" in data:
            config.ai = AIConfig(**data["ai"])
        if "analysis" in data:
            config.analysis = AnalysisConfig(**data["analysis"])
        if "security" in data:
            config.security = SecurityConfig(**data["security"])
        if "output" in data:
            config.output = OutputConfig(**data["output"])
        if "git" in data:
            config.git = GitConfig(**data["git"])
        if "cache" in data:
            config.cache = CacheConfig(**data["cache"])

        if "ignore_patterns" in data:
            config.ignore_patterns = data["ignore_patterns"]
        if "include_patterns" in data:
            config.include_patterns = data["include_patterns"]

        return config

    @classmethod
    def load_from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()

        # AI configuration from environment
        if os.getenv("OPENAI_API_KEY"):
            config.ai.openai_api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY"):
            config.ai.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("AI_PROVIDER"):
            config.ai.provider = os.getenv("AI_PROVIDER", "openai")

        # Git configuration
        if os.getenv("GITHUB_TOKEN"):
            config.git.github_token = os.getenv("GITHUB_TOKEN")

        # Analysis configuration
        if os.getenv("CODE_SAGE_MIN_SEVERITY"):
            config.analysis.min_severity = os.getenv("CODE_SAGE_MIN_SEVERITY", "info")

        return config

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration with priority:
        1. Specified config file
        2. .codesage.yaml in current directory
        3. .codesage.json in current directory
        4. Environment variables
        5. Default configuration
        """
        config = cls()

        # Try to load from file
        if config_path and config_path.exists():
            config = cls.from_file(config_path)
        else:
            # Look for default config files
            for filename in [".codesage.yaml", ".codesage.yml", ".codesage.json"]:
                path = Path.cwd() / filename
                if path.exists():
                    config = cls.from_file(path)
                    break

        # Override with environment variables
        env_config = cls.load_from_env()
        if env_config.ai.openai_api_key:
            config.ai.openai_api_key = env_config.ai.openai_api_key
        if env_config.ai.anthropic_api_key:
            config.ai.anthropic_api_key = env_config.ai.anthropic_api_key
        if env_config.git.github_token:
            config.git.github_token = env_config.git.github_token

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    def save(self, config_path: Path) -> None:
        """Save configuration to file."""
        with open(config_path, "w", encoding="utf-8") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            elif config_path.suffix == ".json":
                json.dump(self.to_dict(), f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Validate AI configuration (now just warnings, not errors)
        # The tool will work without AI, so missing keys are not critical
        # if self.ai.enabled:
        #     if self.ai.provider == "openai" and not self.ai.openai_api_key:
        #         errors.append("Warning: OpenAI API key not set (AI features will be disabled)")
        #     if self.ai.provider == "anthropic" and not self.ai.anthropic_api_key:
        #         errors.append("Warning: Anthropic API key not set (AI features will be disabled)")

        # Validate severity level
        valid_severities = ["info", "low", "medium", "high", "critical"]
        if self.analysis.min_severity not in valid_severities:
            errors.append(f"Invalid min_severity: {self.analysis.min_severity}")

        # Validate output format
        valid_formats = ["rich", "json", "sarif", "junit"]
        if self.output.format not in valid_formats:
            errors.append(f"Invalid output format: {self.output.format}")

        return errors
