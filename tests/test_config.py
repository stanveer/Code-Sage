"""Tests for configuration system."""

import pytest
from pathlib import Path
import tempfile
import yaml

from code_sage.core.config import Config, AIConfig


class TestConfig:
    """Test configuration system."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = Config()
        
        assert config.ai is not None
        assert config.analysis is not None
        assert config.security is not None
        assert config.output is not None

    def test_load_from_yaml(self) -> None:
        """Test loading config from YAML."""
        config_data = {
            "ai": {
                "provider": "openai",
                "enabled": True,
            },
            "analysis": {
                "min_severity": "medium",
            },
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            f.flush()
            
            config = Config.from_file(Path(f.name))
            
            assert config.ai.provider == "openai"
            assert config.analysis.min_severity == "medium"

    def test_validation(self) -> None:
        """Test configuration validation."""
        config = Config()
        config.ai.enabled = True
        config.ai.provider = "openai"
        config.ai.openai_api_key = None
        
        errors = config.validate()
        assert len(errors) > 0
        assert any("API key" in error for error in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
