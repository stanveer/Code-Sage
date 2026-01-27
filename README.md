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

Code Sage is a **production-ready** static code analyzer built with Python that **works immediately with no configuration**. It combines traditional AST-based analysis with optional AI (GPT-4/Claude) to provide intelligent code review, security scanning, and automated fixes.

### Why Code Sage?

- ✅ **No Setup Required**: Works instantly - no API keys, no configuration needed
- ✅ **Comprehensive**: Multi-language support, security scanning, optional AI in one tool
- ✅ **Production Ready**: Fully tested, type-hinted, well-documented code
- ✅ **Privacy First**: Runs 100% locally, AI is optional and only used if you enable it
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

### AI Integration (Optional)
- 🤖 **GPT-4 & Claude**: Context-aware analysis (optional)
- 💬 **Explanations**: Plain English issue descriptions
- 🔧 **Auto-Fix**: AI-suggested code fixes
- 🎯 **Smart**: Focuses on critical issues first
- ⚡ **Works Without AI**: Full analysis capabilities without API keys

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

- **Python 3.8+** (required)
- **API Key** (optional, only for AI features):
  - OpenAI API key **OR**
  - Anthropic API key
  
**Note**: Works perfectly without any API keys!

---

## 📖 Quick Start

### 1. Analyze a Local Project (No Setup Required)

```bash
code-sage analyze myproject/
```

This works immediately with **no configuration** - finds bugs, code smells, and security issues!

### 2. Analyze a GitHub Repository

```bash
code-sage github https://github.com/username/repo
```

Code Sage will clone and analyze any public repository automatically.

### 3. Generate Beautiful Reports

```bash
code-sage analyze myproject/ --output report.html --format html
```

### 4. Optional: Enable AI-Powered Insights

AI features are **completely optional** but provide enhanced explanations and fix suggestions.

```bash
# Set your API key (one-time setup)
export OPENAI_API_KEY="sk-..."

# Or for Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Run with AI enabled
code-sage analyze myproject/ --ai
```

**Note**: The tool works perfectly without AI - AI just adds extra explanations and suggestions!

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

### AI-Powered Analysis (Optional)

**AI features are completely optional!** Code Sage performs full analysis without any API keys.

```bash
# Default: Works without AI (no setup needed)
code-sage analyze .

# Skip AI explicitly (faster)
code-sage analyze . --no-ai

# Enable AI with OpenAI GPT-4 (requires API key)
export OPENAI_API_KEY="sk-..."
code-sage analyze . --ai

# Or use Anthropic Claude (requires API key)
export ANTHROPIC_API_KEY="sk-ant-..."
code-sage analyze . --ai --config claude-config.yaml
```

**Get API Keys (Optional):**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/account/keys

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

## 🤖 AI Features (Optional)

### Do I Need AI?

**No!** Code Sage is fully functional without AI:
- ✅ Finds all bugs, code smells, and security issues
- ✅ Calculates code metrics
- ✅ Generates reports
- ✅ Works 100% locally

### What Does AI Add?

AI provides **enhanced insights**:
- 💬 Plain English explanations of why issues matter
- 🔧 Intelligent fix suggestions with code examples
- 🎯 Context-aware recommendations
- 📚 Learning resources and best practices

### Setting Up AI (Optional)

#### Option 1: Environment Variables (Easiest)

```bash
# For OpenAI (GPT-4)
export OPENAI_API_KEY="sk-proj-..."

# For Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# Then use with --ai flag
code-sage analyze . --ai
```

#### Option 2: Configuration File

Create `.codesage.yaml`:

```yaml
ai:
  enabled: true
  provider: openai  # or 'anthropic'
  openai_api_key: ${OPENAI_API_KEY}  # reads from environment
  openai_model: gpt-4-turbo-preview
  temperature: 0.3
```

Then just run:

```bash
code-sage analyze .  # AI automatically enabled
```

#### Getting API Keys

- **OpenAI**: https://platform.openai.com/api-keys (~$0.03/analysis)
- **Anthropic**: https://console.anthropic.com/account/keys (~$0.02/analysis)

#### Disable AI

```bash
# Explicitly disable (faster, free)
code-sage analyze . --no-ai

# Or in config file
ai:
  enabled: false
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
