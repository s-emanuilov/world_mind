#!/usr/bin/env python3
"""
Run epistemic confusion test with real LLMs via OpenRouter.

Tests a small sample to validate that real LLMs show different behavior
from Graph-RAG on epistemic confusion cards.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path to import evaluation framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from openrouter_adapter import OpenRouterLLMAdapter


def eval_cards_with_llm(cards_path: str, model: str, system_name: str, out_path: str, max_cards: int = None):
    """
    Evaluate cards using OpenRouter LLM.
    
    Args:
        cards_path: Path to input JSONL with cards
        model: OpenRouter model identifier
        system_name: Name for results tracking
        out_path: Output JSONL path
        max_cards: Maximum number of cards to test (for cost control)
    """
    # Create adapter
    adapter = OpenRouterLLMAdapter(model=model)
    
    results = []
    cards_processed = 0
    
    print(f"\n{'='*60}")
    print(f"Evaluating: {system_name}")
    print(f"Model: {model}")
    print(f"Reading cards from: {cards_path}")
    if max_cards:
        print(f"Max cards: {max_cards}")
    print(f"{'='*60}\n")
    
    # Read and process cards
    with open(cards_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if max_cards and cards_processed >= max_cards:
                break
            
            card = json.loads(line)
            
            # Get LLM prediction
            print(f"[{i}/{max_cards or '?'}] Processing {card['id']}... ", end="", flush=True)
            pred = adapter.answer(card)
            print(f"→ {pred}", end="")
            
            # Check correctness
            gold = card["gold"]
            is_correct = (pred == gold)
            
            if is_correct:
                print(" ✓")
            else:
                print(f" ✗ (expected {gold})")
            
            # Store result
            result = {
                "id": card["id"],
                "gold": gold,
                "pred": pred,
                "pass": is_correct,
                "system": system_name,
                "label": card.get("label", "?")
            }
            results.append(result)
            cards_processed += 1
    
    # Write results
    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    
    # Calculate and print summary
    total = len(results)
    correct = sum(r["pass"] for r in results)
    accuracy = correct / total * 100 if total > 0 else 0
    
    # Per-label breakdown
    label_stats = {}
    for label in ["E", "C", "U"]:
        label_results = [r for r in results if r["label"] == label]
        if label_results:
            label_correct = sum(r["pass"] for r in label_results)
            label_accuracy = label_correct / len(label_results) * 100
            label_stats[label] = {
                "total": len(label_results),
                "correct": label_correct,
                "accuracy": label_accuracy
            }
    
    print(f"\n{'='*60}")
    print(f"Evaluation Complete: {system_name}")
    print(f"{'='*60}")
    print(f"Total cards: {total}")
    print(f"Correct: {correct}")
    print(f"Overall Accuracy: {accuracy:.2f}%")
    print(f"\nPer-label breakdown:")
    for label, stats in label_stats.items():
        label_name = {"E": "Entailed", "C": "Contradictory", "U": "Unknown"}[label]
        print(f"  {label} ({label_name}): {stats['correct']}/{stats['total']} = {stats['accuracy']:.1f}%")
    print(f"\nResults saved to: {out_path}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Test real LLMs on epistemic confusion cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Claude on 20 cards
  python run_llm_test.py \\
      --cards ../results/context_cards.jsonl \\
      --model "anthropic/claude-3.5-sonnet" \\
      --name "claude-3.5-sonnet" \\
      --max 20 \\
      --out results/claude_test.jsonl
  
  # Test GPT-4 on 20 cards
  python run_llm_test.py \\
      --cards ../results/context_cards.jsonl \\
      --model "openai/gpt-4" \\
      --name "gpt-4" \\
      --max 20 \\
      --out results/gpt4_test.jsonl
        """
    )
    parser.add_argument("--cards", required=True, help="Input JSONL file with cards")
    parser.add_argument("--model", required=True, help="OpenRouter model identifier")
    parser.add_argument("--name", required=True, help="System name for results")
    parser.add_argument("--out", required=True, help="Output JSONL file for results")
    parser.add_argument("--max", type=int, default=20, help="Max cards to test (default: 20)")
    
    args = parser.parse_args()
    
    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY environment variable not set")
        print("Set it with: export OPENROUTER_API_KEY=your_key_here")
        sys.exit(1)
    
    # Run evaluation
    eval_cards_with_llm(
        cards_path=args.cards,
        model=args.model,
        system_name=args.name,
        out_path=args.out,
        max_cards=args.max
    )


if __name__ == "__main__":
    main()


