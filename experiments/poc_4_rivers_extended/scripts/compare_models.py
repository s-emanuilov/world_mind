#!/usr/bin/env python3
"""
Compare results from multiple LLM evaluations
"""

import json
import os
import glob
from pathlib import Path

def load_summary(results_dir, model_name):
    """Load summary for a specific model."""
    summary_file = os.path.join(results_dir, f"{model_name}_summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            return json.load(f)
    return None

def compare_models(results_dir):
    """Compare results from all evaluated models."""
    results_dir = Path(results_dir)
    summaries = []
    
    # Find all summary files
    for summary_file in results_dir.glob("*_summary.json"):
        model_name = summary_file.stem.replace("_summary", "")
        summary = load_summary(results_dir, model_name)
        if summary:
            summaries.append(summary)
    
    if not summaries:
        print("No evaluation summaries found.")
        return
    
    # Sort by accuracy
    summaries.sort(key=lambda x: x['accuracy'], reverse=True)
    
    print("LLM Evaluation Comparison")
    print("=" * 50)
    print(f"{'Model':<30} {'Questions':<10} {'Correct':<8} {'Accuracy':<10}")
    print("-" * 50)
    
    for summary in summaries:
        print(f"{summary['model']:<30} {summary['total_questions']:<10} {summary['correct_answers']:<8} {summary['accuracy']:.2%}")

if __name__ == "__main__":
    results_dir = '../evaluation'
    compare_models(results_dir)
