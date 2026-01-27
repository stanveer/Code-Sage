# Code Sage 🧙‍♂️

<div align="center">

**Production-ready AI-powered code analyzer that finds bugs, security issues, and suggests improvements**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-brightgreen.svg)](.)

[Features](#-features) •
[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Examples](#-examples)

</div>

---

## 🌟 Overview

Code Sage is a **production-ready**, AI-powered static code analyzer built with Python. It combines traditional AST-based analysis with cutting-edge AI (GPT-4/Claude) to provide intelligent code review, security scanning, and automated fixes.

### Why Code Sage?

- ✅ **Comprehensive**: Multi-language support, security scanning, AI analysis in one tool
- ✅ **Production Ready**: Fully tested, type-hinted, well-documented code
- ✅ **Privacy First**: Runs locally, only uses AI when you want it
- ✅ **Developer Friendly**: Beautiful CLI, rich output, easy configuration
- ✅ **Extensible**: Plugin architecture, custom rules, multiple output formats

---

## ✨ Features

### Core Analysis
- 🔍 **Multi-Language**: Python, JavaScript, TypeScript (extensible)
- 🐛 **Bug Detection**: Mutable defaults, identity checks, type errors
- 💡 **Code Smells**: Complexity, long functions, duplicate code
- 📐 **Metrics**: Cyclomatic complexity, maintainability index, Halstead

### Security Scanning
- 🛡️ **Secrets Detection**: API keys, passwords with entropy analysis
- 🔒 **OWASP Top 10**: SQL injection, XSS, command injection
- 📦 **Dependency CVEs**: Checks npm and pip packages
- 🔐 **Language-Specific**: Pickle, eval, dangerous functions

### AI Integration
- 🤖 **GPT-4 & Claude**: Context-aware analysis
- 💬 **Explanations**: Plain English issue descriptions
- 🔧 **Auto-Fix**: AI-suggested code fixes
- 🎯 **Smart**: Focuses on critical issues first

### Professional CLI
- 🎨 **Beautiful UI**: Rich console with colors and tables
- ⚡ **Fast**: Parallel analysis with caching
- 📊 **Reports**: HTML, JSON, SARIF formats
- 🔄 **Git Integration**: Pre-commit hooks, repo analysis

---

## 🚀 Installation

### From Source

```bash
git clone https://github.com/stanveer/Code-Sage.git
cd Code-Sage
pip install -r requirements.txt
pip install -e .
```

### System Requirements

- Python 3.8+
- Optional: OpenAI API key or Anthropic API key for AI features

---

## 📖 Quick Start

### 1. Analyze a Project

```bash
code-sage analyze myproject/
```

### 2. Analyze a GitHub Repo

```bash
code-sage github https://github.com/username/repo
```

### 3. With AI Analysis

```bash
export OPENAI_API_KEY="sk-..."
code-sage analyze myproject/ --ai
```

### 4. Generate HTML Report

```bash
code-sage analyze myproject/ --output report.html
```

---

## 💻 Usage Examples

### Basic Analysis

```bash
# Analyze current directory
code-sage analyze .

# Analyze specific file
code-sage analyze src/main.py

# Filter by severity (only show critical/high)
code-sage analyze . --severity high

# JSON output
code-sage analyze . --format json --output results.json
```

### Security Scanning

```bash
# Enable security scan
code-sage analyze . --security

# Security only (faster)
code-sage analyze . --security --no-ai
```

### AI-Powered Analysis

```bash
# Use OpenAI GPT-4
export OPENAI_API_KEY="sk-..."
code-sage analyze . --ai

# Use Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."
code-sage analyze . --ai --config claude-config.yaml
```

### Configuration

```bash
# Create config file
code-sage init

# Use custom config
code-sage analyze . --config myconfig.yaml

# Verbose output
code-sage analyze . --verbose
```

---

## ⚙️ Configuration

Create `.codesage.yaml` in your project root:

```yaml
ai:
  enabled: true
  provider: openai  # or anthropic
  openai_api_key: ${OPENAI_API_KEY}
  openai_model: gpt-4-turbo-preview
  temperature: 0.3

analysis:
  enabled_languages:
    - python
    - javascript
    - typescript
  min_severity: medium
  max_complexity: 15
  parallel_analysis: true

security:
  enable_secrets_scan: true
  enable_dependency_scan: true
  enable_owasp_scan: true
  min_entropy_threshold: 4.5

output:
  format: rich
  generate_html: true
  show_ai_explanations: true
  output_dir: ./reports
```

See `.example.codesage.yaml` for all configuration options.

---

## 📊 Example Output

```
$ code-sage analyze examples/

🧙‍♂️ Code Sage v1.0.0
Analyzing: examples/

✓ Analyzing files... (2.3s)
✓ Running security scan... (0.8s)
✓ AI analysis... (4.2s)

┌─────────────────────┬─────────┐
│ Metric              │ Value   │
├─────────────────────┼─────────┤
│ Total Files         │ 2       │
│ Total Issues        │ 23      │
│ Analysis Time       │ 7.3s    │
└─────────────────────┴─────────┘

┌──────────┬───────┐
│ Severity │ Count │
├──────────┼───────┤
│ CRITICAL │   3   │
│ HIGH     │   5   │
│ MEDIUM   │   8   │
│ LOW      │   7   │
└──────────┴───────┘

Top Issues:

1. CRITICAL Hardcoded Secret: API Key
   📁 examples/example.py:11
   Potential hardcoded api key detected

2. HIGH SQL Injection
   📁 examples/example.py:28
   SQL query built with string concatenation
   
3. HIGH Use of eval()
   📁 examples/example.py:45
   Code injection risk via eval
```

---

## 🏗️ Architecture

```
code_sage/
├── core/               # Core engine and models
│   ├── engine.py      # Main analysis engine
│   ├── models.py      # Data models
│   ├── config.py      # Configuration management
│   ├── analyzer.py    # Base analyzer interface
│   ├── aggregator.py  # Issue deduplication & ranking
│   └── pattern_matcher.py  # Pattern matching engine
├── analyzers/         # Language-specific analyzers
│   ├── python_analyzer.py
│   └── javascript_analyzer.py
├── ai/                # AI integration
│   ├── provider.py    # AI provider abstraction
│   └── enrichment.py  # Issue enrichment
├── security/          # Security scanning
│   └── scanner.py     # Security vulnerability detection
├── cli/               # Command-line interface
│   ├── main.py        # CLI entry point
│   └── reporter.py    # Report generation
├── git/               # Git integration
│   └── hooks.py       # Git hooks management
└── utils/             # Utilities
    └── file_utils.py  # File operations
```

---

## 🧪 Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=code_sage --cov-report=html
```

### Run on Examples

```bash
# Analyze example files
code-sage analyze examples/

# Should find ~20+ issues
```

### Code Quality

```bash
# Format code
black code_sage/

# Sort imports
isort code_sage/

# Type check
mypy code_sage/

# Lint
flake8 code_sage/
```

---

## 🎯 Supported Languages

| Language    | Status | Features |
|------------|--------|----------|
| Python     | ✅ Full | AST analysis, complexity, security |
| JavaScript | ✅ Full | Syntax, common issues, security |
| TypeScript | ✅ Full | Same as JavaScript |
| Java       | 🚧 Planned | - |
| Go         | 🚧 Planned | - |
| Rust       | 🚧 Planned | - |

---

## 🛡️ Security Features

### Secrets Detection
- API keys, passwords, tokens
- Entropy analysis (Shannon entropy)
- Configurable patterns
- Support for custom secret patterns

### OWASP Top 10
- SQL Injection
- Cross-Site Scripting (XSS)
- Command Injection
- Insecure Deserialization
- And more...

### Dependency Scanning
- CVE database checks
- Python: `safety` integration
- JavaScript: `npm audit` integration
- Outdated package detection

---

## 📚 Documentation

### Command Reference

```bash
# Main commands
code-sage analyze <path>      # Analyze code
code-sage github <url>         # Analyze GitHub repo
code-sage init                 # Create config file
code-sage report <path>        # Generate report

# Options
--config PATH       # Custom config file
--output PATH       # Output file
--format FORMAT     # Output format (rich/json/sarif)
--severity LEVEL    # Min severity (info/low/medium/high/critical)
--ai / --no-ai     # Enable/disable AI
--security         # Enable security scan
--verbose          # Verbose output
--debug            # Debug mode
```

### Exit Codes

- `0` - Success, no critical issues
- `1` - Critical issues found
- `2` - Analysis error

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

### Adding a New Language Analyzer

1. Create `code_sage/analyzers/your_language_analyzer.py`
2. Extend `BaseAnalyzer` class
3. Implement `analyze_file()` method
4. Register in `engine.py`

### Adding Custom Rules

Create a `.codesage-rules.yaml`:

```yaml
rules:
  - id: custom-rule-1
    name: "No TODO comments"
    pattern: "# TODO"
    severity: low
    category: maintainability
    languages: [python, javascript]
```

---

## 📈 Roadmap

- [x] Python analyzer
- [x] JavaScript/TypeScript analyzer
- [x] AI integration (GPT-4, Claude)
- [x] Security scanning
- [x] HTML reports
- [ ] VS Code extension
- [ ] JetBrains IDE plugin
- [ ] Web dashboard
- [ ] More language support (Java, Go, Rust)
- [ ] Auto-fix implementation
- [ ] CI/CD integrations

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/), [Rich](https://rich.readthedocs.io/), and [Radon](https://radon.readthedocs.io/)
- AI powered by OpenAI and Anthropic
- Inspired by tools like SonarQube, CodeClimate, and Bandit

---

## 🎉 Try It Now!

```bash
git clone https://github.com/stanveer/Code-Sage.git
cd Code-Sage
pip install -r requirements.txt
pip install -e .

# Analyze the examples
code-sage analyze examples/

# See what Code Sage can do! 🧙‍♂️
```

---

<div align="center">

[⭐ Star us on GitHub](https://github.com/stanveer/Code-Sage) •
[🐛 Report Bug](https://github.com/stanveer/Code-Sage/issues) •
[💡 Request Feature](https://github.com/stanveer/Code-Sage/issues)

</div>
