"""
FKB Validation Report Generator
Creates comprehensive HTML validation reports from validation results.
"""

from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json


def generate_html_report(validation_results: Dict[str, Any],
                        dataset_name: str = "FKB Dataset",
                        output_path: str = "validation_report.html") -> str:
    """
    Generate comprehensive HTML validation report.

    Args:
        validation_results: Results from validate_dataset()
        dataset_name: Name of the dataset being validated
        output_path: Path to save HTML report

    Returns:
        Path to generated report
    """

    # Calculate severity counts
    critical_count = sum(
        1 for e in validation_results.get('header_errors', [])
        if 'SOSI-001' in e or 'SOSI-006' in e
    )
    critical_count += sum(
        1 for f in validation_results.get('feature_errors', [])
        for errors in f.get('errors', {}).values()
        for e in errors
        if any(code in e for code in ['ATTR-002', 'GEOM-001', 'TOPO-001', 'TOPO-005'])
    )

    high_count = validation_results['summary']['total_errors'] - critical_count
    feature_count = validation_results['summary']['total_features']
    error_count = validation_results['summary']['total_errors']

    # Determine overall status
    if critical_count > 0:
        status = "CRITICAL"
        status_color = "#d32f2f"
        status_icon = "❌"
    elif error_count > feature_count * 0.1:  # More than 10% have errors
        status = "FAIL"
        status_color = "#f57c00"
        status_icon = "⚠️"
    elif error_count > 0:
        status = "PASS WITH WARNINGS"
        status_color = "#fbc02d"
        status_icon = "⚠️"
    else:
        status = "PASS"
        status_color = "#388e3c"
        status_icon = "✅"

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FKB Validation Report - {dataset_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        .header .subtitle {{
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .status-banner {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}

        .status-icon {{
            font-size: 4rem;
        }}

        .status-content {{
            flex: 1;
        }}

        .status-content h2 {{
            font-size: 2rem;
            color: {status_color};
            margin-bottom: 0.5rem;
        }}

        .status-content .status-detail {{
            color: #666;
            font-size: 0.95rem;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .metric-card .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }}

        .metric-card .metric-label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .metric-card.critical .metric-value {{
            color: #d32f2f;
        }}

        .metric-card.high .metric-value {{
            color: #f57c00;
        }}

        .metric-card.info .metric-value {{
            color: #1976d2;
        }}

        .section {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .section h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }}

        .error-list {{
            list-style: none;
        }}

        .error-item {{
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #f57c00;
            background: #fff3e0;
            border-radius: 4px;
        }}

        .error-item.critical {{
            border-left-color: #d32f2f;
            background: #ffebee;
        }}

        .error-item .error-code {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #d32f2f;
            margin-right: 0.5rem;
        }}

        .error-item .error-message {{
            color: #333;
        }}

        .feature-error {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: #f9f9f9;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }}

        .feature-error .feature-header {{
            font-weight: bold;
            margin-bottom: 0.75rem;
            color: #333;
        }}

        .feature-error .error-category {{
            margin-top: 0.75rem;
            padding-left: 1rem;
        }}

        .feature-error .error-category h4 {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
        }}

        .feature-error .error-category ul {{
            list-style: none;
            padding-left: 0;
        }}

        .feature-error .error-category li {{
            padding: 0.5rem;
            margin-bottom: 0.25rem;
            background: white;
            border-radius: 3px;
            border-left: 3px solid #f57c00;
            font-size: 0.85rem;
        }}

        .no-errors {{
            color: #388e3c;
            font-weight: bold;
            padding: 1rem;
            text-align: center;
            background: #e8f5e9;
            border-radius: 4px;
        }}

        .footer {{
            text-align: center;
            color: #666;
            padding: 2rem;
            font-size: 0.85rem;
        }}

        .collapsible {{
            cursor: pointer;
            user-select: none;
        }}

        .collapsible:hover {{
            background: #f5f5f5;
        }}

        .collapse-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}

        .collapse-content.active {{
            max-height: 5000px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .section, .metric-card, .status-banner {{
                box-shadow: none;
                border: 1px solid #e0e0e0;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{status_icon} FKB Validation Report</h1>
        <div class="subtitle">
            Dataset: {dataset_name} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>

    <div class="container">
        <div class="status-banner">
            <div class="status-icon">{status_icon}</div>
            <div class="status-content">
                <h2>{status}</h2>
                <div class="status-detail">
                    Validated {feature_count:,} features with {error_count:,} total errors
                </div>
            </div>
        </div>

        <div class="metrics">
            <div class="metric-card info">
                <div class="metric-value">{feature_count:,}</div>
                <div class="metric-label">Total Features</div>
            </div>
            <div class="metric-card critical">
                <div class="metric-value">{critical_count:,}</div>
                <div class="metric-label">Critical Errors</div>
            </div>
            <div class="metric-card high">
                <div class="metric-value">{high_count:,}</div>
                <div class="metric-label">High Priority Errors</div>
            </div>
            <div class="metric-card info">
                <div class="metric-value">{len(validation_results.get('feature_errors', [])):,}</div>
                <div class="metric-label">Features with Errors</div>
            </div>
        </div>
"""

    # Header Errors Section
    header_errors = validation_results.get('header_errors', [])
    if header_errors:
        html += """
        <div class="section">
            <h3>📋 Header (SOSI .HODE) Errors</h3>
            <ul class="error-list">
"""
        for error in header_errors:
            is_critical = 'SOSI-001' in error or 'SOSI-006' in error
            error_class = 'critical' if is_critical else ''
            html += f'                <li class="error-item {error_class}">{error}</li>\n'

        html += """            </ul>
        </div>
"""

    # Feature Errors Section
    feature_errors = validation_results.get('feature_errors', [])
    if feature_errors:
        # Only show first 50 to avoid huge reports
        display_errors = feature_errors[:50]
        html += f"""
        <div class="section">
            <h3>🔍 Feature Errors ({len(feature_errors):,} features with errors)</h3>
"""
        if len(feature_errors) > 50:
            html += f'            <p style="color: #f57c00; margin-bottom: 1rem;">Showing first 50 of {len(feature_errors)} features with errors</p>\n'

        for feat_error in display_errors:
            objtype = feat_error.get('objtype', 'Unknown')
            feat_index = feat_error.get('feature_index', 0)
            errors_dict = feat_error.get('errors', {})

            html += f"""
            <div class="feature-error">
                <div class="feature-header">
                    Feature #{feat_index}: {objtype} ({feat_error.get('error_count', 0)} errors)
                </div>
"""

            for category, error_list in errors_dict.items():
                if error_list:
                    html += f"""
                <div class="error-category">
                    <h4>{category.replace('_', ' ').title()}</h4>
                    <ul>
"""
                    for error in error_list:
                        html += f'                        <li>{error}</li>\n'

                    html += """                    </ul>
                </div>
"""

            html += """            </div>
"""

        html += """        </div>
"""
    else:
        html += """
        <div class="section">
            <h3>🔍 Feature Errors</h3>
            <div class="no-errors">✅ No feature errors found!</div>
        </div>
"""

    # Topology Errors Section
    topology_errors = validation_results.get('topology_errors', [])
    if topology_errors:
        html += """
        <div class="section">
            <h3>🔗 Topology Errors</h3>
            <ul class="error-list">
"""
        for error in topology_errors[:100]:  # Limit to 100
            html += f'                <li class="error-item">{error}</li>\n'

        if len(topology_errors) > 100:
            html += f'                <li class="error-item">... and {len(topology_errors) - 100} more topology errors</li>\n'

        html += """            </ul>
        </div>
"""

    # Recommendations Section
    html += f"""
        <div class="section">
            <h3>💡 Recommendations</h3>
            <ul style="padding-left: 2rem; line-height: 2;">
"""

    if critical_count > 0:
        html += """                <li><strong>🔴 CRITICAL:</strong> Fix all critical errors before using this dataset in production.</li>
"""

    if header_errors:
        html += """                <li><strong>📋 Header:</strong> Correct SOSI header errors - these affect the entire dataset.</li>
"""

    if len(feature_errors) > feature_count * 0.5:
        html += """                <li><strong>⚠️ High Error Rate:</strong> More than 50% of features have errors. Consider re-processing the source data.</li>
"""

    if topology_errors:
        html += """                <li><strong>🔗 Topology:</strong> Fix topology errors to ensure proper spatial relationships (networks, shared boundaries).</li>
"""

    if error_count == 0:
        html += """                <li><strong>✅ Excellent:</strong> Dataset passed all validation checks. Ready for production use!</li>
"""

    html += """            </ul>
        </div>

        <div class="section">
            <h3>📚 Validation Details</h3>
            <ul style="padding-left: 2rem; line-height: 1.8;">
                <li><strong>Validators Run:</strong> Attributes, Geometry, Accuracy, Metadata, Topology</li>
                <li><strong>Rules Source:</strong> FKB 5.1 Specifications (extracted YAML rules)</li>
                <li><strong>Error Codes:</strong>
                    <ul style="margin-top: 0.5rem; padding-left: 2rem;">
                        <li>ATTR-xxx: Attribute validation errors</li>
                        <li>GEOM-xxx: Geometry validation errors</li>
                        <li>ACC-xxx: Accuracy standard errors</li>
                        <li>META-xxx: Metadata/KVALITET errors</li>
                        <li>SOSI-xxx: SOSI format errors</li>
                        <li>TOPO-xxx: Topology validation errors</li>
                    </ul>
                </li>
            </ul>
        </div>
    </div>

    <div class="footer">
        Generated by FKB Validation Tools | GEO-MCP Server<br>
        Based on FKB 5.1 Specifications
    </div>

    <script>
        // Add collapse functionality for large error lists
        document.querySelectorAll('.collapsible').forEach(element => {{
            element.addEventListener('click', function() {{
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('active');
            }});
        }});
    </script>
</body>
</html>
"""

    # Write to file
    output_path = Path(output_path)
    output_path.write_text(html, encoding='utf-8')

    return str(output_path)


def generate_json_report(validation_results: Dict[str, Any],
                        output_path: str = "validation_report.json") -> str:
    """
    Generate machine-readable JSON validation report.

    Args:
        validation_results: Results from validate_dataset()
        output_path: Path to save JSON report

    Returns:
        Path to generated report
    """
    # Add metadata
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'validator_version': '1.0.0',
            'fkb_version': '5.1'
        },
        'results': validation_results
    }

    output_path = Path(output_path)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    return str(output_path)


def generate_summary_report(validation_results: Dict[str, Any]) -> str:
    """
    Generate short text summary suitable for CLI output.

    Args:
        validation_results: Results from validate_dataset()

    Returns:
        Summary string
    """
    feature_count = validation_results['summary']['total_features']
    error_count = validation_results['summary']['total_errors']
    feature_error_count = len(validation_results.get('feature_errors', []))

    if error_count == 0:
        status_icon = "✅"
        status = "PASS"
    elif error_count < feature_count * 0.1:
        status_icon = "⚠️"
        status = "PASS WITH WARNINGS"
    else:
        status_icon = "❌"
        status = "FAIL"

    summary = f"""
{status_icon} FKB VALIDATION REPORT
{'=' * 60}

Status: {status}
Features Validated: {feature_count:,}
Features with Errors: {feature_error_count:,}
Total Errors: {error_count:,}

Breakdown:
- Header Errors: {len(validation_results.get('header_errors', []))}
- Feature Errors: {feature_error_count}
- Topology Errors: {len(validation_results.get('topology_errors', []))}

"""

    if error_count > 0:
        summary += "\n⚠️  Please review the detailed HTML report for specifics.\n"
    else:
        summary += "\n✅ Dataset is valid and ready for production use!\n"

    return summary
