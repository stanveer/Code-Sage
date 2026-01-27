# Contributing to Code Sage 🧙‍♂️

Thank you for your interest in contributing to Code Sage! This document provides guidelines for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/yourusername/Code-Sage.git`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Install dependencies**: `pip install -r requirements.txt`
5. **Make your changes**
6. **Run tests**: `pytest tests/ -v`
7. **Submit a pull request**

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install dev dependencies
pip install pytest pytest-cov black isort flake8 mypy
```

## Code Standards

### Python Code Style
- Follow PEP 8
- Use Black for formatting: `black code_sage/`
- Use isort for imports: `isort code_sage/`
- Maximum line length: 100 characters

### Type Hints
- All functions must have type hints
- Use `typing` module for complex types
- Example:
```python
def analyze_file(self, file_path: Path) -> FileAnalysis:
    """Analyze a file."""
    pass
```

### Documentation
- All modules, classes, and functions must have docstrings
- Use Google-style docstrings
- Example:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input
    """
    pass
```

## Testing

### Writing Tests
- Place tests in `tests/` directory
- Test file names must start with `test_`
- Use pytest for testing

```python
def test_feature():
    """Test description."""
    # Arrange
    analyzer = PythonAnalyzer()
    
    # Act
    result = analyzer.analyze_file(Path("test.py"))
    
    # Assert
    assert result.success
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_python_analyzer.py -v

# With coverage
pytest tests/ --cov=code_sage --cov-report=html
```

## Adding a New Language Analyzer

1. Create `code_sage/analyzers/your_language_analyzer.py`
2. Extend `BaseAnalyzer`:

```python
from code_sage.core.analyzer import BaseAnalyzer
from code_sage.core.models import FileAnalysis

class YourLanguageAnalyzer(BaseAnalyzer):
    def get_language(self) -> str:
        return "your_language"
    
    def can_analyze(self, file_path: Path) -> bool:
        return file_path.suffix in [".ext"]
    
    def analyze_file(self, file_path: Path) -> FileAnalysis:
        # Implementation
        pass
```

3. Register in `code_sage/core/engine.py`:

```python
def _register_default_analyzers(self) -> None:
    from code_sage.analyzers.your_language_analyzer import YourLanguageAnalyzer
    self.registry.register(YourLanguageAnalyzer(self.config))
```

4. Add tests in `tests/test_your_language_analyzer.py`

## Adding Custom Pattern Rules

Add patterns to `code_sage/core/pattern_matcher.py`:

```python
PatternRule(
    id="your-rule-id",
    name="Your Rule Name",
    description="Rule description",
    pattern=r'your regex pattern',
    severity=IssueSeverity.MEDIUM,
    category=IssueCategory.SECURITY,
    languages=["python", "javascript"],
    message="Issue message",
    fix_suggestion="How to fix",
)
```

## Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples
```
feat(analyzer): add Go language support

- Implement Go AST parser
- Add Go-specific patterns
- Add tests for Go analyzer

Closes #123
```

## Pull Request Process

1. Update README.md with details of changes if needed
2. Update CHANGELOG.md with your changes
3. Ensure all tests pass
4. Update documentation
5. Request review from maintainers

## Code Review

- Be respectful and constructive
- Focus on the code, not the person
- Explain your reasoning
- Be open to feedback

## Questions?

Open an issue or reach out to maintainers!

Thank you for contributing! 🎉
