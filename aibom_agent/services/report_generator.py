"""Report generator for creating HTML reports from analysis results."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger

from ..models.analysis_result import AnalysisResult, ComparisonResult


class ReportGenerator:
    """Service for generating HTML reports from AIBOM analysis results."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
            autoescape=True
        )
        
        # Create templates directory if it doesn't exist
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Create default templates
        self._create_default_templates()
    
    async def generate_single_model_report(self, result: AnalysisResult) -> str:
        """
        Generate HTML report for a single model analysis.
        
        Args:
            result: AnalysisResult to generate report for
            
        Returns:
            Path to the generated HTML report
        """
        logger.info(f"Generating single model report for: {result.model_name}")
        
        try:
            # Prepare template data
            template_data = {
                'result': result,
                'model_name': result.model_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'report_type': 'single_model'
            }
            
            # Render template
            template = self.jinja_env.get_template('single_model_report.html')
            html_content = template.render(**template_data)
            
            # Save report
            report_filename = f"aibom_report_{result.model_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Single model report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate single model report: {e}")
            raise
    
    async def generate_comparison_report(self, result: ComparisonResult) -> str:
        """
        Generate HTML report for model comparison.
        
        Args:
            result: ComparisonResult to generate report for
            
        Returns:
            Path to the generated HTML report
        """
        logger.info(f"Generating comparison report for {len(result.model_names)} models")
        
        try:
            # Prepare template data
            template_data = {
                'result': result,
                'model_names': result.model_names,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'report_type': 'comparison'
            }
            
            # Render template
            template = self.jinja_env.get_template('comparison_report.html')
            html_content = template.render(**template_data)
            
            # Save report
            models_str = "_vs_".join([name.replace('/', '_') for name in result.model_names])
            report_filename = f"aibom_comparison_{models_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Comparison report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate comparison report: {e}")
            raise
    
    def _create_default_templates(self) -> None:
        """Create default HTML templates if they don't exist."""
        
        # Single model report template
        single_model_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIBOM Report - {{ model_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007acc; padding-bottom: 20px; margin-bottom: 30px; }
        .model-info { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .security-analysis { background: #fff3cd; padding: 20px; border-radius: 5px; margin-bottom: 30px; border-left: 4px solid #ffc107; }
        .risk-high { border-left-color: #dc3545; background: #f8d7da; }
        .risk-medium { border-left-color: #ffc107; background: #fff3cd; }
        .risk-low { border-left-color: #28a745; background: #d4edda; }
        .components { margin-bottom: 30px; }
        .component { background: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .vulnerability { background: #f8d7da; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #dc3545; }
        .recommendation { background: #d1ecf1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #17a2b8; }
        h1, h2, h3 { color: #333; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-high { background: #dc3545; color: white; }
        .badge-medium { background: #ffc107; color: black; }
        .badge-low { background: #28a745; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Bill of Materials Report</h1>
            <h2>{{ model_name }}</h2>
            <p><strong>Generated:</strong> {{ timestamp }}</p>
        </div>
        
        <div class="model-info">
            <h3>📋 Model Information</h3>
            <p><strong>Author:</strong> {{ result.model_info.author }}</p>
            <p><strong>License:</strong> {{ result.model_info.license or 'Not specified' }}</p>
            <p><strong>Downloads:</strong> {{ result.model_info.downloads }}</p>
            <p><strong>Pipeline:</strong> {{ result.model_info.pipeline_tag or 'Not specified' }}</p>
            <p><strong>Library:</strong> {{ result.model_info.library_name or 'Not specified' }}</p>
            <p><strong>Tags:</strong> {{ result.model_info.tags | join(', ') }}</p>
        </div>
        
        <div class="security-analysis risk-{{ result.security_analysis.risk_level.lower() }}">
            <h3>🔒 Security Analysis</h3>
            <p><strong>Risk Score:</strong> {{ result.security_analysis.risk_score }}/10</p>
            <p><strong>Risk Level:</strong> <span class="badge badge-{{ result.security_analysis.risk_level.lower() }}">{{ result.security_analysis.risk_level }}</span></p>
            
            {% if result.security_analysis.vulnerabilities %}
            <h4>⚠️ Vulnerabilities ({{ result.security_analysis.vulnerabilities | length }})</h4>
            {% for vuln in result.security_analysis.vulnerabilities %}
            <div class="vulnerability">
                <strong>{{ vuln.get('type', 'Unknown') }}</strong>: {{ vuln.get('description', 'No description') }}
                {% if vuln.get('cve_id') %}<br><small>CVE: {{ vuln.cve_id }}</small>{% endif %}
            </div>
            {% endfor %}
            {% endif %}
            
            {% if result.security_analysis.recommendations %}
            <h4>💡 Recommendations</h4>
            {% for rec in result.security_analysis.recommendations %}
            <div class="recommendation">{{ rec }}</div>
            {% endfor %}
            {% endif %}
        </div>
        
        <div class="components">
            <h3>🔧 Components ({{ result.aibom.components | length }})</h3>
            {% for component in result.aibom.components %}
            <div class="component">
                <strong>{{ component.get('name', 'Unknown') }}</strong> 
                <small>({{ component.get('type', 'unknown') }})</small>
                <br>{{ component.get('description', 'No description') }}
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p><small>Generated by AIBOM Agent System using AWS AgentCore Runtime</small></p>
        </div>
    </div>
</body>
</html>
        """
        
        # Comparison report template
        comparison_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIBOM Comparison Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007acc; padding-bottom: 20px; margin-bottom: 30px; }
        .comparison-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .model-card { background: #f8f9fa; padding: 20px; border-radius: 5px; border-left: 4px solid #007acc; }
        .insights { background: #e7f3ff; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .common-components { background: #d4edda; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .unique-components { background: #fff3cd; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .security-comparison { background: #f8d7da; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        h1, h2, h3 { color: #333; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-high { background: #dc3545; color: white; }
        .badge-medium { background: #ffc107; color: black; }
        .badge-low { background: #28a745; color: white; }
        .component-list { max-height: 200px; overflow-y: auto; }
        .component-item { background: white; padding: 10px; margin: 5px 0; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 AI Model Comparison Report</h1>
            <h2>{{ model_names | join(' vs ') }}</h2>
            <p><strong>Generated:</strong> {{ timestamp }}</p>
            <p><strong>Models Analyzed:</strong> {{ model_names | length }}</p>
        </div>
        
        <div class="insights">
            <h3>🧠 AI-Generated Insights</h3>
            <p><strong>Summary:</strong> {{ result.insights.summary }}</p>
            
            {% if result.insights.key_differences %}
            <h4>🔑 Key Differences</h4>
            <ul>
            {% for diff in result.insights.key_differences %}
                <li>{{ diff }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            <p><strong>Risk Assessment:</strong> {{ result.insights.risk_assessment }}</p>
        </div>
        
        <div class="comparison-grid">
            {% for individual_result in result.individual_results %}
            <div class="model-card">
                <h3>{{ individual_result.model_name }}</h3>
                <p><strong>Risk Level:</strong> <span class="badge badge-{{ individual_result.security_analysis.risk_level.lower() }}">{{ individual_result.security_analysis.risk_level }}</span></p>
                <p><strong>Risk Score:</strong> {{ individual_result.security_analysis.risk_score }}/10</p>
                <p><strong>Components:</strong> {{ individual_result.aibom.components | length }}</p>
                <p><strong>Vulnerabilities:</strong> {{ individual_result.security_analysis.vulnerabilities | length }}</p>
                <p><strong>License:</strong> {{ individual_result.model_info.license or 'Not specified' }}</p>
            </div>
            {% endfor %}
        </div>
        
        <div class="common-components">
            <h3>🤝 Common Components ({{ result.comparison.common_components | length }})</h3>
            <div class="component-list">
                {% for component in result.comparison.common_components %}
                <div class="component-item">
                    <strong>{{ component.get('name', 'Unknown') }}</strong> - {{ component.get('type', 'unknown') }}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="unique-components">
            <h3>🎯 Unique Components</h3>
            {% for model_name, components in result.comparison.unique_components.items() %}
            <h4>{{ model_name }} ({{ components | length }} unique)</h4>
            <div class="component-list">
                {% for component in components %}
                <div class="component-item">
                    <strong>{{ component.get('name', 'Unknown') }}</strong> - {{ component.get('type', 'unknown') }}
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        
        <div class="security-comparison">
            <h3>🔒 Security Comparison</h3>
            <p><strong>Highest Risk Model:</strong> {{ result.comparison.security_comparison.get('highest_risk_model', 'N/A') }}</p>
            <p><strong>Lowest Risk Model:</strong> {{ result.comparison.security_comparison.get('lowest_risk_model', 'N/A') }}</p>
            
            {% if result.insights.security_recommendations %}
            <h4>Security Recommendations</h4>
            <ul>
            {% for rec in result.insights.security_recommendations %}
                <li>{{ rec }}</li>
            {% endfor %}
            </ul>
            {% endif %}
        </div>
        
        <div class="footer">
            <p><small>Generated by AIBOM Agent System using AWS AgentCore Runtime</small></p>
        </div>
    </div>
</body>
</html>
        """
        
        # Write templates to files
        single_template_path = self.templates_dir / "single_model_report.html"
        comparison_template_path = self.templates_dir / "comparison_report.html"
        
        if not single_template_path.exists():
            with open(single_template_path, 'w', encoding='utf-8') as f:
                f.write(single_model_template)
        
        if not comparison_template_path.exists():
            with open(comparison_template_path, 'w', encoding='utf-8') as f:
                f.write(comparison_template)