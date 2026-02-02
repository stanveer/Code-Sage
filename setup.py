"""Setup script for Code Sage."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="code-sage-ai",
    version="1.0.0",
    description="AI-powered code analyzer that finds bugs, suggests improvements, and fixes issues",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Code Sage Team",
    author_email="team@codesage.dev",
    url="https://github.com/stanveer/Code-Sage",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.7.0",
        "pyyaml>=6.0.1",
        "toml>=0.10.2",
        "astroid>=3.0.0",
        "esprima>=4.0.1",
        "tree-sitter>=0.20.4",
        "radon>=6.0.1",
        "bandit>=1.7.5",
        "safety>=3.0.0",
        "openai>=1.10.0",
        "anthropic>=0.18.0",
        "GitPython>=3.1.41",
        "PyGithub>=2.1.1",
        "jinja2>=3.1.3",
        "plotly>=5.18.0",
        "kaleido>=0.2.1",
        "weasyprint>=60.2",
        "colorama>=0.4.6",
        "prompt-toolkit>=3.0.43",
        "requests>=2.31.0",
        "python-dotenv>=1.0.1",
        "typing-extensions>=4.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=24.1.0",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "tox>=4.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code-sage=code_sage.cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="code analysis, static analysis, linting, security, ai, code quality",
)
