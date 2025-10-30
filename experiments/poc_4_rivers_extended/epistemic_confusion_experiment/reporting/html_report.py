#!/usr/bin/env python3
"""
Generate an extended HTML report from:
- results.jsonl (evaluation results, potentially multiple systems)
- metrics.json (computed abstention metrics)

Outputs a comprehensive HTML report with:
- Summary metrics table
- Confusion matrices per system
- Detailed per-card results
- Visualizations (if matplotlib available)
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def load_json(path: str) -> Optional[Dict]:
    """Load JSON file if it exists."""
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: str) -> List[Dict]:
    """Load JSONL file."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def format_metric(value: Optional[float], precision: int = 3) -> str:
    """Format metric for HTML display."""
    if value is None:
        return "—"
    return f"{value:.{precision}f}"


def generate_html(results: List[Dict], metrics: Dict) -> str:
    """Generate HTML report content."""
    html = []
    
    # Header
    html.append("""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WorldMind – Epistemic Confusion Experiment Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            margin: 0;
            padding: 2rem;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a1a1a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        h2 {
            color: #333;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.3rem;
        }
        h3 {
            color: #555;
            margin-top: 1.5rem;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            background: white;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 0.6rem 0.8rem;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .metric-high {
            color: #0a8a0a;
            font-weight: 600;
        }
        .metric-low {
            color: #cc0000;
            font-weight: 600;
        }
        .metric-mid {
            color: #666;
        }
        .confusion-matrix {
            display: inline-block;
            margin: 1rem 0;
        }
        .confusion-matrix td {
            text-align: center;
            min-width: 80px;
        }
        .confusion-matrix th {
            text-align: center;
            font-weight: 600;
        }
        .label-E { background-color: #d4edda; }
        .label-C { background-color: #f8d7da; }
        .label-U { background-color: #fff3cd; }
        .pass { color: #0a8a0a; font-weight: 600; }
        .fail { color: #cc0000; font-weight: 600; }
        .summary-box {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
            border-left: 4px solid #0066cc;
        }
        .metric-explanation {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
            margin-top: 0.5rem;
        }
        code {
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
<div class="container">
""")
    
    # Title and introduction
    html.append("<h1>WorldMind – Epistemic Confusion Experiment Results</h1>")
    html.append("""
    <div class="summary-box">
        <p><strong>Experiment:</strong> Testing abstention precision via context cards with three epistemic states:</p>
        <ul>
            <li><strong>E (Entailed):</strong> Facts present in knowledge graph</li>
            <li><strong>C (Contradictory):</strong> Facts that violate constraints or are explicitly negated</li>
            <li><strong>U (Unknown):</strong> Facts not present and not provably wrong (open-world)</li>
        </ul>
        <p><strong>Goal:</strong> Measure systems' ability to abstain when appropriate (high AP, CVRR) 
        while maintaining answer accuracy on entailed facts (high LA).</p>
    </div>
    """)
    
    # Systems overview
    systems = sorted(set(r["system"] for r in results))
    html.append(f"<p><strong>Systems evaluated:</strong> {', '.join(systems)}</p>")
    html.append(f"<p><strong>Total test cards:</strong> {len(results) // len(systems) if systems else len(results)}</p>")
    
    # ========================================
    # Summary Metrics Table
    # ========================================
    html.append("<h2>Summary Metrics</h2>")
    html.append('<p class="metric-explanation">Key metrics for evaluating abstention behavior:</p>')
    html.append("<table>")
    html.append("<tr>")
    html.append("<th>System</th>")
    html.append("<th>AP<br/><small>(Abstention Precision)</small></th>")
    html.append("<th>CVRR<br/><small>(Constraint Violation Reject)</small></th>")
    html.append("<th>FAR-NE<br/><small>(False Answer on Non-Entailed)</small></th>")
    html.append("<th>LA<br/><small>(Licensed Answer Accuracy)</small></th>")
    html.append("<th>Coverage<br/><small>(% Answered)</small></th>")
    html.append("<th>Overall<br/><small>(Accuracy)</small></th>")
    html.append("</tr>")
    
    for sys in systems:
        m = metrics.get(sys, {}).get("metrics", {})
        html.append("<tr>")
        html.append(f"<td><strong>{sys}</strong></td>")
        html.append(f"<td class='{_metric_class(m.get('AP'), higher_better=True)}'>{format_metric(m.get('AP'))}</td>")
        html.append(f"<td class='{_metric_class(m.get('CVRR'), higher_better=True)}'>{format_metric(m.get('CVRR'))}</td>")
        html.append(f"<td class='{_metric_class(m.get('FAR_NE'), higher_better=False)}'>{format_metric(m.get('FAR_NE'))}</td>")
        html.append(f"<td class='{_metric_class(m.get('LA'), higher_better=True)}'>{format_metric(m.get('LA'))}</td>")
        html.append(f"<td>{format_metric(m.get('coverage'))}</td>")
        html.append(f"<td>{format_metric(m.get('overall_accuracy'))}</td>")
        html.append("</tr>")
    
    html.append("</table>")
    
    # Metric definitions
    html.append("""
    <div class="metric-explanation">
        <strong>Metric Definitions:</strong>
        <ul>
            <li><strong>AP (Abstention Precision):</strong> Of all abstentions, what fraction were correct?</li>
            <li><strong>CVRR:</strong> Of contradictory cases, what fraction were rejected?</li>
            <li><strong>FAR-NE:</strong> Of non-entailed cases, how often did system answer incorrectly? (lower is better)</li>
            <li><strong>LA:</strong> Of entailed cases, what fraction were answered correctly?</li>
        </ul>
    </div>
    """)
    
    # ========================================
    # Confusion Matrices
    # ========================================
    html.append("<h2>Confusion Matrices</h2>")
    html.append("<p>Breakdown of actions (Answer/Abstain) vs ground truth (E/C/U):</p>")
    
    for sys in systems:
        cm = metrics.get(sys, {}).get("confusion_matrix", {})
        if not cm:
            continue
        
        html.append(f"<h3>{sys}</h3>")
        html.append('<table class="confusion-matrix">')
        html.append("<tr><th></th><th>E (Entailed)</th><th>C (Contradictory)</th><th>U (Unknown)</th></tr>")
        html.append(f"<tr><th>ANSWER</th><td>{cm.get('A_E', 0)}</td><td>{cm.get('A_C', 0)}</td><td>{cm.get('A_U', 0)}</td></tr>")
        html.append(f"<tr><th>ABSTAIN</th><td>{cm.get('S_E', 0)}</td><td>{cm.get('S_C', 0)}</td><td>{cm.get('S_U', 0)}</td></tr>")
        html.append("</table>")
    
    # ========================================
    # Detailed Metrics Breakdown
    # ========================================
    html.append("<h2>Detailed Metrics by System</h2>")
    
    for sys in systems:
        data = metrics.get(sys, {})
        m = data.get("metrics", {})
        totals = data.get("totals", {})
        
        html.append(f"<h3>{sys}</h3>")
        html.append("<table>")
        html.append("<tr><th>Metric</th><th>Value</th><th>Description</th></tr>")
        
        metric_rows = [
            ("AP (overall)", m.get("AP"), "Precision of abstentions"),
            ("AP on invalid (C)", m.get("AP_invalid"), "Precision on contradictory claims"),
            ("AP on unknown (U)", m.get("AP_unknown"), "Precision on unknown claims"),
            ("AR (overall)", m.get("AR"), "Recall of abstentions"),
            ("AR on contradictory", m.get("AR_contradictory"), "Recall on contradictory claims"),
            ("AR on unknown", m.get("AR_unknown"), "Recall on unknown claims"),
            ("CVRR", m.get("CVRR"), "Constraint violation rejection rate"),
            ("FAR-NE", m.get("FAR_NE"), "False answer rate on non-entailed"),
            ("LA", m.get("LA"), "Licensed answer accuracy"),
            ("Coverage", m.get("coverage"), "Fraction of claims answered"),
            ("Answer accuracy", m.get("answer_accuracy"), "Accuracy when answering (not abstaining)"),
            ("Overall accuracy", m.get("overall_accuracy"), "Overall correctness rate"),
        ]
        
        for name, value, desc in metric_rows:
            html.append(f"<tr><td><strong>{name}</strong></td><td>{format_metric(value)}</td><td>{desc}</td></tr>")
        
        html.append("</table>")
        
        # Totals
        html.append("<p><strong>Test set breakdown:</strong> ")
        html.append(f"Entailed: {totals.get('entailed', 0)}, ")
        html.append(f"Contradictory: {totals.get('contradictory', 0)}, ")
        html.append(f"Unknown: {totals.get('unknown', 0)}")
        html.append("</p>")
    
    # ========================================
    # Sample Results
    # ========================================
    html.append("<h2>Sample Results (First 100 Cards)</h2>")
    html.append("<table>")
    html.append("<tr><th>Card ID</th><th>System</th><th>Label</th><th>Gold</th><th>Prediction</th><th>Result</th></tr>")
    
    for r in results[:100]:
        pass_class = "pass" if r.get("pass") else "fail"
        label_class = f"label-{r.get('label', '?')}"
        html.append(f"<tr class='{label_class}'>")
        html.append(f"<td><code>{r['id']}</code></td>")
        html.append(f"<td>{r['system']}</td>")
        html.append(f"<td><strong>{r.get('label', '?')}</strong></td>")
        html.append(f"<td>{r['gold']}</td>")
        html.append(f"<td>{r['pred']}</td>")
        html.append(f"<td class='{pass_class}'>{'✓' if r.get('pass') else '✗'}</td>")
        html.append("</tr>")
    
    html.append("</table>")
    
    # Footer
    html.append("""
    <div class="summary-box" style="margin-top: 2rem;">
        <p><strong>Interpretation:</strong></p>
        <ul>
            <li>High <strong>AP</strong> and <strong>CVRR</strong> indicate the system correctly identifies when to abstain</li>
            <li>Low <strong>FAR-NE</strong> means the system rarely answers incorrectly on non-entailed claims</li>
            <li>High <strong>LA</strong> ensures the system still answers correctly on entailed facts</li>
            <li>Graph-licensed systems should excel at all four metrics compared to statistical baselines</li>
        </ul>
    </div>
    """)
    
    html.append("</div></body></html>")
    
    return "".join(html)


def _metric_class(value: Optional[float], higher_better: bool = True) -> str:
    """Determine CSS class for metric value."""
    if value is None:
        return ""
    
    if higher_better:
        if value >= 0.8:
            return "metric-high"
        elif value <= 0.5:
            return "metric-low"
        else:
            return "metric-mid"
    else:
        # Lower is better
        if value <= 0.2:
            return "metric-high"
        elif value >= 0.5:
            return "metric-low"
        else:
            return "metric-mid"


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML report from evaluation results and metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--results", required=True, help="JSONL file with evaluation results")
    parser.add_argument("--metrics", required=True, help="JSON file with computed metrics")
    parser.add_argument("--out", default="report.html", help="Output HTML file path")
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading results from: {args.results}")
    results = load_jsonl(args.results)
    print(f"Loaded {len(results)} result rows")
    
    print(f"Loading metrics from: {args.metrics}")
    metrics = load_json(args.metrics)
    
    if not metrics:
        print("ERROR: Could not load metrics file")
        return
    
    # Generate HTML
    print("Generating HTML report...")
    html_content = generate_html(results, metrics)
    
    # Write output
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n{'='*60}")
    print(f"HTML report generated successfully!")
    print(f"Output: {output_path.absolute()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()


