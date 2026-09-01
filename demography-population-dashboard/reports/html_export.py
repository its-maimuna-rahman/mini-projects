"""
Standalone HTML Dashboard Export Engine
Generates self-contained, offline-compatible HTML dashboard reports
strictly formatted to the "Claude-pilled" warm cream, terracotta, and soft white design brief.
"""

from __future__ import annotations
import html
from typing import Dict, Any, Optional
from engine.pipeline import DemographicPipelineResult
from ui.components import render_calm_gauge_html


def generate_standalone_html_dashboard(
    result: DemographicPipelineResult,
    pyramid_html_div: Optional[str] = None,
) -> str:
    """
    Constructs a standalone HTML document containing the full demographic evaluation,
    calm bell-curve gauges, quality diagnostic cards, and full 22-measure tables.
    """
    gauges_html = ""
    for code, m in result.measures.items():
        interp = m.interpretation or {}
        gauges_html += render_calm_gauge_html(
            measure_name=m.name,
            value=m.raw_value,
            formatted_value=m.formatted_value,
            unit=m.unit,
            status=interp.get("status", "MODERATE"),
            status_label=interp.get("label", "Standard"),
            gauge_min=interp.get("gauge_min", 0.0),
            gauge_max=interp.get("gauge_max", 100.0),
            source=interp.get("source", "Standard"),
            is_heuristic=interp.get("is_heuristic", False),
        )
        
    concerns_html = ""
    for c in result.top_concerns:
        sev = c.get("severity", "WARNING")
        bg_col = "#FCECE7" if sev in ("CRITICAL", "SEVERE") else "#FAF0EA"
        txt_col = "#C05621" if sev in ("CRITICAL", "SEVERE") else "#CC785C"
        concerns_html += f"""
        <div style="background: {bg_col}; border: 1px solid rgba(204,120,92,0.3); border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-weight: 700; color: {txt_col}; font-size: 15px; margin-bottom: 4px;">{html.escape(c.get('title', ''))}</div>
            <div style="font-size: 13.5px; color: #1F1B16; line-height: 1.4;">{html.escape(c.get('description', ''))}</div>
            <div style="font-size: 12.5px; color: #6B655C; margin-top: 6px; font-style: italic;">{html.escape(c.get('recommendation', ''))}</div>
        </div>
        """
        
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vital Stats Suite — {html.escape(result.dataset_name)}</title>
    <style>
        body {{
            background-color: #F5F1EA;
            color: #1F1B16;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 32px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            font-family: Georgia, "Playfair Display", serif;
            font-weight: normal;
            color: #1F1B16;
        }}
        h1 {{
            font-size: 32px;
            margin-bottom: 6px;
        }}
        .meta-bar {{
            font-size: 14px;
            color: #CC785C;
            margin-bottom: 24px;
            font-weight: 500;
        }}
        .card {{
            background: #FFFFFF;
            border: 1px solid #E5DFD3;
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 24px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            margin-top: 12px;
        }}
        th, td {{
            text-align: left;
            padding: 10px 12px;
            border-bottom: 1px solid #E5DFD3;
        }}
        th {{
            font-family: Georgia, serif;
            font-weight: 600;
            color: #1F1B16;
            background: #FAF7F2;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 600;
        }}
        .badge-excellent {{ background: #EBF5F3; color: #2A9D8F; }}
        .badge-good {{ background: #EEF4F7; color: #4A6B82; }}
        .badge-warning {{ background: #FAF0EA; color: #CC785C; }}
        .badge-critical {{ background: #FCECE7; color: #C05621; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Vital Statistics Suite</h1>
        <div class="meta-bar">Dataset: {html.escape(result.dataset_name)} &bull; Year: {result.year or 'Current'} &bull; {result.computable_count} / {result.total_measures_target} Measures Computed</div>
        
        <div class="card">
            <h2>Executive Synthesis & Top Findings</h2>
            <p style="font-size: 15px; color: #1F1B16;">{html.escape(result.executive_summary)}</p>
            {concerns_html}
        </div>
        
        {f'<div class="card"><h2>Population Pyramid</h2>{pyramid_html_div}</div>' if pyramid_html_div else ''}
        
        <div class="card">
            <h2>Core Demographic Indicators & Calm Gauge Horizon</h2>
            {gauges_html}
        </div>
        
        <div class="card">
            <h2>Data Quality & Coverage Audits</h2>
            <table>
                <thead>
                    <tr>
                        <th>Diagnostic Check</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Interpretation</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td><strong>{html.escape(q.name)}</strong></td>
                        <td>{f"{q.score:.2f}" if q.score is not None else "N/A"}</td>
                        <td><span class="badge badge-{q.status.lower()}">{q.status}</span></td>
                        <td>{html.escape(q.interpretation)}</td>
                    </tr>
                    ''' for q in result.quality_checks.values()])}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>Complete 22 Demographic Measures Inventory</h2>
            <table>
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Measure Name</th>
                        <th>Computed Value</th>
                        <th>Status</th>
                        <th>Standard Formula</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td><strong>{m.code}</strong></td>
                        <td>{m.name}</td>
                        <td><strong>{m.formatted_value}</strong></td>
                        <td><span class="badge badge-{(m.interpretation.get('status','good')).lower()}">{m.interpretation.get('status','Standard')}</span></td>
                        <td><small style="color: #6B655C;">{m.formula}</small></td>
                    </tr>
                    ''' for m in result.measures.values()])}
                </tbody>
            </table>
        </div>
        
        <div style="text-align: center; color: #8A8175; font-size: 12px; margin-top: 32px;">
            Generated with Vital Stats Suite &bull; Google Antigravity
        </div>
    </div>
</body>
</html>
    """
    return doc
