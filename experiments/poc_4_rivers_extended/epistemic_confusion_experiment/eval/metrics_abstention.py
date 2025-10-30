#!/usr/bin/env python3
"""
Compute abstention metrics from result JSONL files.

Metrics computed:
- AP (Abstention Precision): overall and by type
- AR (Abstention Recall): overall and by type  
- CVRR (Constraint Violation Rejection Rate): S_C / (S_C + A_C)
- FAR-NE (False Answer Rate on Non-Entailed): (A_C + A_U) / all non-entailed
- LA (Licensed Answer Accuracy on E): A_E / (A_E + S_E)

Confusion matrix (Action × Truth):
              E (entailed)  C (contradictory)  U (unknown)
ANSWER          A_E              A_C              A_U
ABSTAIN         S_E              S_C              S_U

Gold mapping:
- YES → E (Entailed)
- NO → C (Contradictory)  
- UNKNOWN → U (Unknown)

Prediction mapping:
- YES/NO → ANSWER (A)
- UNKNOWN → ABSTAIN (S)
"""

import argparse
import json
import collections
from pathlib import Path
from typing import Dict, List


def compute_metrics(rows: List[Dict]) -> Dict:
    """
    Compute abstention metrics for each system in the results.
    
    Args:
        rows: List of result dictionaries with keys: id, gold, pred, system, label
        
    Returns:
        Dictionary mapping system names to their metrics
    """
    out_by_sys = {}
    
    # Group by system
    systems = set(r["system"] for r in rows)
    
    for sys in sorted(systems):
        system_rows = [r for r in rows if r["system"] == sys]
        
        # Build confusion matrix
        counts = collections.Counter()
        
        for r in system_rows:
            gold = r["gold"]  # YES/NO/UNKNOWN
            pred = r["pred"]  # YES/NO/UNKNOWN
            
            # Map gold to epistemic label
            if gold == "YES":
                label = "E"  # Entailed
            elif gold == "NO":
                label = "C"  # Contradictory
            else:
                label = "U"  # Unknown
            
            # Map prediction to action
            if pred == "UNKNOWN":
                action = "S"  # Abstain (Silent)
            else:
                action = "A"  # Answer
            
            # Increment count for (action, label) pair
            key = f"{action}_{label}"
            counts[key] += 1
        
        # Extract counts from confusion matrix
        A_E = counts.get("A_E", 0)  # Answered when Entailed
        A_C = counts.get("A_C", 0)  # Answered when Contradictory
        A_U = counts.get("A_U", 0)  # Answered when Unknown
        S_E = counts.get("S_E", 0)  # Abstained when Entailed
        S_C = counts.get("S_C", 0)  # Abstained when Contradictory
        S_U = counts.get("S_U", 0)  # Abstained when Unknown
        
        # Total counts
        total_entailed = A_E + S_E
        total_contradictory = A_C + S_C
        total_unknown = A_U + S_U
        total_non_entailed = total_contradictory + total_unknown
        total_abstentions = S_E + S_C + S_U
        total_answers = A_E + A_C + A_U
        
        # ========================================
        # Primary Metrics
        # ========================================
        
        # AP (Abstention Precision): Of all abstentions, what fraction were correct?
        # Correct abstentions are S_C and S_U (should abstain on non-entailed)
        # Incorrect abstentions are S_E (should not abstain on entailed)
        AP = (S_C + S_U) / total_abstentions if total_abstentions > 0 else None
        
        # AP by type
        AP_invalid = S_C / (S_C + S_E) if (S_C + S_E) > 0 else None  # Precision on contradictory
        AP_unknown = S_U / (S_U + S_E) if (S_U + S_E) > 0 else None  # Precision on unknown
        
        # AR (Abstention Recall): Of all non-entailed, how many did we catch?
        AR = (S_C + S_U) / total_non_entailed if total_non_entailed > 0 else None
        
        # AR by type
        AR_contradictory = S_C / total_contradictory if total_contradictory > 0 else None
        AR_unknown = S_U / total_unknown if total_unknown > 0 else None
        
        # CVRR (Constraint Violation Rejection Rate): 
        # Of contradictory cases, what fraction did we reject?
        CVRR = S_C / total_contradictory if total_contradictory > 0 else None
        
        # FAR-NE (False Answer Rate on Non-Entailed):
        # Of all non-entailed cases, how often did we answer (incorrectly)?
        FAR_NE = (A_C + A_U) / total_non_entailed if total_non_entailed > 0 else None
        
        # LA (Licensed Answer Accuracy):
        # Of all entailed cases, what fraction did we answer correctly?
        LA = A_E / total_entailed if total_entailed > 0 else None
        
        # Coverage: Fraction of claims answered (vs abstained)
        coverage = total_answers / len(system_rows) if len(system_rows) > 0 else None
        
        # Accuracy among answers (when not abstaining)
        # For this, we need to check which answers were correct
        # A_E is correct, A_C and A_U are incorrect
        answer_accuracy = A_E / total_answers if total_answers > 0 else None
        
        # Overall accuracy (including abstentions as incorrect on E, correct on C/U)
        # Correct: A_E (answered correctly) + S_C (abstained correctly) + S_U (abstained correctly)
        overall_accuracy = (A_E + S_C + S_U) / len(system_rows) if len(system_rows) > 0 else None
        
        # Store results
        out_by_sys[sys] = {
            "counts": dict(counts),
            "confusion_matrix": {
                "A_E": A_E, "A_C": A_C, "A_U": A_U,
                "S_E": S_E, "S_C": S_C, "S_U": S_U
            },
            "totals": {
                "entailed": total_entailed,
                "contradictory": total_contradictory,
                "unknown": total_unknown,
                "non_entailed": total_non_entailed,
                "abstentions": total_abstentions,
                "answers": total_answers
            },
            "metrics": {
                "AP": AP,
                "AP_invalid": AP_invalid,
                "AP_unknown": AP_unknown,
                "AR": AR,
                "AR_contradictory": AR_contradictory,
                "AR_unknown": AR_unknown,
                "CVRR": CVRR,
                "FAR_NE": FAR_NE,
                "LA": LA,
                "coverage": coverage,
                "answer_accuracy": answer_accuracy,
                "overall_accuracy": overall_accuracy
            }
        }
    
    return out_by_sys


def print_metrics_report(metrics: Dict):
    """Print a human-readable report of the metrics."""
    for sys, data in metrics.items():
        print(f"\n{'='*70}")
        print(f"System: {sys}")
        print(f"{'='*70}")
        
        # Confusion matrix
        cm = data["confusion_matrix"]
        print(f"\nConfusion Matrix (Action × Truth):")
        print(f"{'':10s} {'E':>10s} {'C':>10s} {'U':>10s}")
        print(f"{'ANSWER':10s} {cm['A_E']:10d} {cm['A_C']:10d} {cm['A_U']:10d}")
        print(f"{'ABSTAIN':10s} {cm['S_E']:10d} {cm['S_C']:10d} {cm['S_U']:10d}")
        
        # Key metrics
        m = data["metrics"]
        print(f"\nKey Metrics:")
        print(f"  Abstention Precision (AP):        {_fmt(m['AP'])}")
        print(f"    - AP on invalid (C):             {_fmt(m['AP_invalid'])}")
        print(f"    - AP on unknown (U):             {_fmt(m['AP_unknown'])}")
        print(f"  Abstention Recall (AR):           {_fmt(m['AR'])}")
        print(f"    - AR on contradictory (C):       {_fmt(m['AR_contradictory'])}")
        print(f"    - AR on unknown (U):             {_fmt(m['AR_unknown'])}")
        print(f"  Constraint Violation Reject Rate: {_fmt(m['CVRR'])}")
        print(f"  False Answer Rate (Non-Entailed): {_fmt(m['FAR_NE'])}")
        print(f"  Licensed Answer Accuracy (LA):    {_fmt(m['LA'])}")
        print(f"\nCoverage & Accuracy:")
        print(f"  Coverage (% answered):            {_fmt(m['coverage'])}")
        print(f"  Accuracy when answering:          {_fmt(m['answer_accuracy'])}")
        print(f"  Overall accuracy:                 {_fmt(m['overall_accuracy'])}")


def _fmt(value, precision=3):
    """Format a metric value for display."""
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"


def main():
    parser = argparse.ArgumentParser(
        description="Compute abstention metrics from evaluation results",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--results", required=True, 
                       help="JSONL file with results (can contain multiple systems)")
    parser.add_argument("--out", required=True,
                       help="Output JSON file for computed metrics")
    parser.add_argument("--verbose", action="store_true",
                       help="Print detailed report to console")
    
    args = parser.parse_args()
    
    # Read results
    print(f"Reading results from: {args.results}")
    rows = []
    with open(args.results, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    
    print(f"Loaded {len(rows)} result rows")
    
    # Compute metrics
    metrics = compute_metrics(rows)
    
    # Write output
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to: {args.out}")
    
    # Print report if verbose
    if args.verbose:
        print_metrics_report(metrics)
    else:
        # Print summary
        for sys, data in metrics.items():
            m = data["metrics"]
            print(f"\n{sys}:")
            print(f"  AP={_fmt(m['AP'])}, CVRR={_fmt(m['CVRR'])}, "
                  f"FAR-NE={_fmt(m['FAR_NE'])}, LA={_fmt(m['LA'])}")


if __name__ == "__main__":
    main()


