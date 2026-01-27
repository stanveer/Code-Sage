"""Report generation for analysis results."""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from jinja2 import Template

from code_sage.core.models import AnalysisResult
from code_sage.core.logger import get_logger


class ReportGenerator:
    """Generate analysis reports in various formats."""

    def __init__(self) -> None:
        """Initialize report generator."""
        self.logger = get_logger()

    def generate_html(self, result: AnalysisResult, output_path: Path) -> None:
        """
        Generate HTML report.

        Args:
            result: Analysis result
            output_path: Output file path
        """
        template = self._get_html_template()
        
        html_content = template.render(
            result=result,
            severity_counts=result.get_severity_counts(),
            category_counts=result.get_category_counts(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        
        output_path.write_text(html_content, encoding="utf-8")
        self.logger.info(f"HTML report generated: {output_path}")

    def generate_json(self, result: AnalysisResult, output_path: Path) -> None:
        """Generate JSON report."""
        data = result.to_dict()
        json_str = json.dumps(data, indent=2)
        output_path.write_text(json_str, encoding="utf-8")
        self.logger.info(f"JSON report generated: {output_path}")

    def generate_sarif(self, result: AnalysisResult, output_path: Path) -> None:
        """Generate SARIF format report."""
        # SARIF format specification: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
        sarif = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Code Sage",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/stanveer/Code-Sage",
                        }
                    },
                    "results": self._convert_to_sarif_results(result),
                }
            ],
        }
        
        json_str = json.dumps(sarif, indent=2)
        output_path.write_text(json_str, encoding="utf-8")
        self.logger.info(f"SARIF report generated: {output_path}")

    def _convert_to_sarif_results(self, result: AnalysisResult) -> list:
        """Convert issues to SARIF results format."""
        sarif_results = []
        
        level_map = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "none",
        }
        
        for issue in result.get_all_issues():
            sarif_result = {
                "ruleId": issue.rule_id or issue.id,
                "level": level_map.get(issue.severity.value, "warning"),
                "message": {
                    "text": issue.description
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": issue.location.file_path
                            },
                            "region": {
                                "startLine": issue.location.line_start,
                                "endLine": issue.location.line_end,
                            }
                        }
                    }
                ],
            }
            
            if issue.suggested_fix:
                sarif_result["fixes"] = [
                    {
                        "description": {
                            "text": issue.fix_description or "Suggested fix"
                        }
                    }
                ]
            
            sarif_results.append(sarif_result)
        
        return sarif_results

    def _get_html_template(self) -> Template:
        """Get HTML template."""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Sage Analysis Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 10px; }
        .timestamp { color: #7f8c8d; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .summary-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
        .summary-card h3 { font-size: 14px; opacity: 0.9; margin-bottom: 10px; }
        .summary-card .value { font-size: 32px; font-weight: bold; }
        .severity-section { margin-bottom: 40px; }
        .severity-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px; }
        .severity-card { padding: 15px; border-radius: 8px; text-align: center; }
        .severity-card.critical { background: #fee; border-left: 4px solid #e74c3c; }
        .severity-card.high { background: #ffeded; border-left: 4px solid #e67e22; }
        .severity-card.medium { background: #fff9e6; border-left: 4px solid #f39c12; }
        .severity-card.low { background: #e8f4f8; border-left: 4px solid #3498db; }
        .severity-card.info { background: #f0f0f0; border-left: 4px solid #95a5a6; }
        .severity-card .count { font-size: 28px; font-weight: bold; margin-bottom: 5px; }
        .severity-card .label { font-size: 12px; text-transform: uppercase; color: #7f8c8d; }
        .issues-list { margin-top: 30px; }
        .issue { background: #f8f9fa; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #3498db; }
        .issue.critical { border-left-color: #e74c3c; }
        .issue.high { border-left-color: #e67e22; }
        .issue.medium { border-left-color: #f39c12; }
        .issue-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
        .issue-title { font-size: 18px; font-weight: 600; color: #2c3e50; }
        .issue-severity { padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
        .issue-severity.critical { background: #e74c3c; color: white; }
        .issue-severity.high { background: #e67e22; color: white; }
        .issue-severity.medium { background: #f39c12; color: white; }
        .issue-severity.low { background: #3498db; color: white; }
        .issue-severity.info { background: #95a5a6; color: white; }
        .issue-location { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }
        .issue-description { margin-bottom: 15px; line-height: 1.6; }
        .code-snippet { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5; }
        h2 { color: #2c3e50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #ecf0f1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧙‍♂️ Code Sage Analysis Report</h1>
        <div class="timestamp">Generated on {{ timestamp }}</div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Files</h3>
                <div class="value">{{ result.total_files }}</div>
            </div>
            <div class="summary-card">
                <h3>Total Issues</h3>
                <div class="value">{{ result.total_issues }}</div>
            </div>
            <div class="summary-card">
                <h3>Analysis Time</h3>
                <div class="value">{{ "%.2f"|format(result.total_time) }}s</div>
            </div>
        </div>
        
        <div class="severity-section">
            <h2>Issues by Severity</h2>
            <div class="severity-grid">
                {% for severity, count in severity_counts.items() %}
                <div class="severity-card {{ severity }}">
                    <div class="count">{{ count }}</div>
                    <div class="label">{{ severity }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="issues-list">
            <h2>All Issues</h2>
            {% for issue in result.get_all_issues()[:50] %}
            <div class="issue {{ issue.severity.value }}">
                <div class="issue-header">
                    <div class="issue-title">{{ issue.title }}</div>
                    <span class="issue-severity {{ issue.severity.value }}">{{ issue.severity.value }}</span>
                </div>
                <div class="issue-location">📁 {{ issue.location }}</div>
                <div class="issue-description">{{ issue.description }}</div>
                {% if issue.code_snippet %}
                <pre class="code-snippet">{{ issue.code_snippet }}</pre>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""
        return Template(template_str)
