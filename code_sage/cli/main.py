"""Main CLI interface for Code Sage."""

import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from code_sage.core.config import Config
from code_sage.core.engine import AnalysisEngine
from code_sage.core.logger import setup_logging
from code_sage.core.models import IssueSeverity
from code_sage.ai.enrichment import AIEnrichment
from code_sage.security.scanner import SecurityScanner, DependencyScanner
from code_sage import __version__


console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx: click.Context, config: str, verbose: bool, debug: bool) -> None:
    """
    Code Sage - AI-powered code analyzer.
    
    Analyze your code for bugs, security issues, and improvements.
    """
    # Setup logging
    setup_logging(verbose=verbose, debug=debug)
    
    # Load configuration
    config_path = Path(config) if config else None
    ctx.obj = {
        "config": Config.load(config_path),
        "verbose": verbose,
        "debug": debug,
    }


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for report")
@click.option("--format", "-f", type=click.Choice(["rich", "json", "sarif", "junit"]), default="rich", help="Output format")
@click.option("--severity", "-s", type=click.Choice(["info", "low", "medium", "high", "critical"]), help="Minimum severity level")
@click.option("--ai/--no-ai", default=False, help="Enable AI-powered analysis (requires API key)")
@click.option("--security/--no-security", default=True, help="Enable security scanning")
@click.option("--fix", is_flag=True, help="Auto-fix issues where possible")
@click.pass_context
def analyze(ctx: click.Context, path: str, output: str, format: str, severity: str, ai: bool, security: bool, fix: bool) -> None:
    """Analyze code in a file or directory."""
    config = ctx.obj["config"]
    path_obj = Path(path)
    
    console.print(Panel.fit(
        f"[bold cyan]Code Sage[/bold cyan] v{__version__}\n"
        f"Analyzing: [yellow]{path}[/yellow]",
        border_style="cyan"
    ))
    
    # Create engine
    engine = AnalysisEngine(config)
    
    # Analyze
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        
        result = engine.analyze_path(path_obj)
        
        progress.update(task, completed=True)
    
    # Security scan
    if security:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running security scan...", total=None)
            
            scanner = SecurityScanner(config)
            dep_scanner = DependencyScanner(config)
            
            # Scan files
            for file_analysis in result.file_analyses:
                security_issues = scanner.scan_file(Path(file_analysis.file_path))
                file_analysis.issues.extend(security_issues)
            
            # Scan dependencies
            dep_issues = dep_scanner.scan_dependencies(path_obj)
            if dep_issues and result.file_analyses:
                result.file_analyses[0].issues.extend(dep_issues)
            
            progress.update(task, completed=True)
    
    # AI enrichment
    if ai:
        # Enable AI in config if requested via CLI
        config.ai.enabled = True
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("AI analysis...", total=None)
            
            try:
                enrichment = AIEnrichment(config)
                if enrichment.provider:
                    all_issues = result.get_all_issues()
                    enriched_issues = enrichment.enrich_issues(all_issues, max_issues=10)
                    progress.update(task, completed=True)
                else:
                    progress.update(task, completed=True)
                    console.print("[yellow]⚠️  AI analysis skipped: No API key configured[/yellow]")
                    console.print("[dim]Tip: Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable[/dim]")
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠️  AI analysis failed: {e}[/yellow]")
    
    # Filter by severity
    if severity:
        severity_enum = IssueSeverity(severity)
        for file_analysis in result.file_analyses:
            file_analysis.issues = [
                issue for issue in file_analysis.issues
                if issue.severity.value >= severity_enum.value
            ]
    
    # Display results
    if format == "rich":
        display_results_rich(result)
    elif format == "json":
        display_results_json(result, output)
    elif format == "sarif":
        console.print("[yellow]SARIF format not yet implemented[/yellow]")
    elif format == "junit":
        console.print("[yellow]JUnit format not yet implemented[/yellow]")
    
    # Auto-fix
    if fix:
        console.print("\n[yellow]Auto-fix mode not yet fully implemented[/yellow]")
    
    # Exit with error code if critical issues found
    critical_count = len(result.get_issues_by_severity(IssueSeverity.CRITICAL))
    if critical_count > 0:
        sys.exit(1)


@cli.command()
@click.argument("url")
@click.option("--branch", "-b", default="main", help="Git branch to analyze")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--ai/--no-ai", default=False, help="Enable AI-powered analysis (requires API key)")
@click.option("--security/--no-security", default=True, help="Enable security scanning")
@click.pass_context
def github(ctx: click.Context, url: str, branch: str, output: str, ai: bool, security: bool) -> None:
    """Analyze a GitHub repository."""
    import tempfile
    import shutil
    from git import Repo
    
    config = ctx.obj["config"]
    
    console.print(f"[cyan]Cloning repository:[/cyan] {url}")
    
    # Clone repository
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            Repo.clone_from(url, tmpdir, branch=branch, depth=1)
            console.print("[green]✓[/green] Repository cloned")
            
            # Analyze (pass through ai and security flags)
            ctx.invoke(analyze, path=tmpdir, output=output, ai=ai, security=security, format="rich", severity=None, fix=False)
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize Code Sage configuration."""
    config_file = Path(".codesage.yaml")
    
    if config_file.exists():
        console.print("[yellow]Configuration file already exists[/yellow]")
        return
    
    # Create default config
    config = Config()
    config.save(config_file)
    
    console.print(f"[green]✓[/green] Created configuration file: {config_file}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="./report.html", help="Output HTML file")
@click.pass_context
def report(ctx: click.Context, path: str, output: str) -> None:
    """Generate an HTML report."""
    console.print("[yellow]HTML report generation not yet fully implemented[/yellow]")
    console.print(f"Would generate report for: {path}")
    console.print(f"Output: {output}")


def display_results_rich(result) -> None:
    """Display results in rich format."""
    console.print()
    
    # Summary
    summary_table = Table(title="Analysis Summary", show_header=False)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    
    summary_table.add_row("Total Files", str(result.total_files))
    summary_table.add_row("Total Issues", str(result.total_issues))
    summary_table.add_row("Analysis Time", f"{result.total_time:.2f}s")
    
    console.print(summary_table)
    console.print()
    
    # Issues by severity
    severity_counts = result.get_severity_counts()
    
    severity_table = Table(title="Issues by Severity")
    severity_table.add_column("Severity", style="bold")
    severity_table.add_column("Count", justify="right")
    
    severity_colors = {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "blue",
        "info": "cyan",
    }
    
    for severity, count in severity_counts.items():
        if count > 0:
            color = severity_colors.get(severity, "white")
            severity_table.add_row(
                f"[{color}]{severity.upper()}[/{color}]",
                f"[{color}]{count}[/{color}]"
            )
    
    console.print(severity_table)
    console.print()
    
    # Top issues
    issues = result.get_all_issues()
    if issues:
        console.print("[bold]Top Issues:[/bold]\n")
        
        for i, issue in enumerate(issues[:10], 1):
            color = severity_colors.get(issue.severity.value, "white")
            console.print(
                f"{i}. [{color}]{issue.severity.value.upper()}[/{color}] "
                f"{issue.title}"
            )
            console.print(f"   [dim]{issue.location}[/dim]")
            console.print(f"   {issue.description}\n")


def display_results_json(result, output_path: str = None) -> None:
    """Display results in JSON format."""
    import json
    
    data = result.to_dict()
    json_str = json.dumps(data, indent=2)
    
    if output_path:
        Path(output_path).write_text(json_str)
        console.print(f"[green]✓[/green] Results written to: {output_path}")
    else:
        console.print(json_str)


if __name__ == "__main__":
    cli()
