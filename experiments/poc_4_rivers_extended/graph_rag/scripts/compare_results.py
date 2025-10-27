#!/usr/bin/env python3
"""
Compare Graph-RAG results with baseline RAG.
"""

import json
import os
import argparse
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

def load_summary(file_path: str) -> dict:
    """Load evaluation summary."""
    with open(file_path, 'r') as f:
        return json.load(f)

def compare_results():
    """Compare Graph-RAG vs baseline RAG results."""
    
    # Graph-RAG summary
    graph_rag_summary = os.path.join(EXPERIMENT_DIR, "results", "graph_rag_summary.json")
    
    # Baseline RAG summary
    baseline_summary = os.path.join(
        os.path.dirname(EXPERIMENT_DIR), "rag_experiment", "results",
        "rag_google_gemini-2.5-flash-lite_summary.json"
    )
    
    if not os.path.exists(graph_rag_summary):
        print("ERROR: Graph-RAG results not found")
        print(f"Expected: {graph_rag_summary}")
        print("Run 'make evaluate' first")
        sys.exit(1)
    
    if not os.path.exists(baseline_summary):
        print("ERROR: Baseline RAG results not found")
        print(f"Expected: {baseline_summary}")
        print("Run the baseline RAG experiment first")
        sys.exit(1)
    
    graph_results = load_summary(graph_rag_summary)
    baseline_results = load_summary(baseline_summary)
    
    print("=" * 60)
    print("Graph-RAG vs Baseline RAG Comparison")
    print("=" * 60)
    print()
    
    print("Baseline RAG (Embedding-based):")
    print(f"  Total Questions: {baseline_results['total_questions']}")
    print(f"  Correct Answers: {baseline_results['correct_answers']}")
    print(f"  Accuracy: {baseline_results['accuracy']:.2%}")
    print()
    
    print("Graph-RAG (Verification-enabled):")
    print(f"  Total Questions: {graph_results['total_questions']}")
    print(f"  Correct Answers: {graph_results['correct_answers']}")
    print(f"  Accuracy: {graph_results['accuracy']:.2%}")
    print()
    
    # Calculate improvement
    improvement = graph_results['accuracy'] - baseline_results['accuracy']
    rel_improvement = (improvement / baseline_results['accuracy']) * 100 if baseline_results['accuracy'] > 0 else 0
    
    print("Improvement:")
    print(f"  Absolute: {improvement:+.2%}")
    print(f"  Relative: {rel_improvement:+.1f}%")
    print()
    
    if improvement > 0:
        print("✓ Graph-RAG is superior!")
    elif improvement < 0:
        print("✗ Graph-RAG underperformed")
    else:
        print("≈ Both methods perform equally")
    
    print("=" * 60)
    
    # Save comparison
    comparison = {
        'baseline_rag': baseline_results,
        'graph_rag': graph_results,
        'improvement': {
            'absolute': improvement,
            'relative': rel_improvement
        }
    }
    
    comparison_path = os.path.join(EXPERIMENT_DIR, "results", "comparison.json")
    with open(comparison_path, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\nComparison saved to: {comparison_path}")

if __name__ == "__main__":
    compare_results()
