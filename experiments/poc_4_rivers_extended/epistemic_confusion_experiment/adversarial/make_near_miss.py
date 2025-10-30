#!/usr/bin/env python3
"""
Generate near-miss adversarial test cases from knowledge graph.

Near-miss cases pair each subject with a plausible but incorrect object,
creating semantically coherent but factually false claims.

All near-miss cards have:
- gold="NO" (false claim)
- label="C" (contradictory)

These test cases stress-test the system's ability to distinguish between
coherent-sounding claims and actually entailed facts.
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Tuple
from rdflib import Graph, URIRef


def extract_label(uri: str) -> str:
    """Extract human-readable label from URI."""
    if '#' in uri:
        return uri.split('#')[-1].replace('_', ' ')
    elif '/' in uri:
        return uri.split('/')[-1].replace('_', ' ')
    return uri


def get_triples(g: Graph, pred: URIRef) -> List[Tuple[str, str]]:
    """Extract all (subject, object) pairs for a given predicate."""
    return [(str(s), str(o)) for s, o in g.subject_objects(pred)]


def format_fact(subj: str, pred_label: str, obj: str) -> str:
    """Format a triple as a human-readable fact statement."""
    subj_label = extract_label(subj)
    obj_label = extract_label(obj)
    return f"{subj_label} {pred_label} {obj_label}"


def format_question(subj: str, pred_label: str, obj: str) -> str:
    """Format a triple as a yes/no question."""
    subj_label = extract_label(subj)
    obj_label = extract_label(obj)
    return f"Is {obj_label} the {pred_label} of {subj_label}?"


def main():
    parser = argparse.ArgumentParser(
        description="Generate near-miss adversarial test cases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 500 near-miss cases for hasMouth predicate
  python make_near_miss.py \\
      --kg ../graph_rag/data/knowledge_graph.ttl \\
      --pred "http://worldmind.ai/rivers-v4#hasMouth" \\
      --pred-label "mouth" \\
      --num 500 \\
      --out ../results/near_miss_cards.jsonl
        """
    )
    parser.add_argument("--kg", required=True, help="Path to knowledge graph (TTL)")
    parser.add_argument("--pred", required=True, help="Predicate IRI to generate near-misses for")
    parser.add_argument("--pred-label", default="related to", help="Human-readable predicate label")
    parser.add_argument("--out", required=True, help="Output JSONL file")
    parser.add_argument("--num", type=int, default=500, help="Number of near-miss cards to generate")
    parser.add_argument("--seed", type=int, default=2027, help="Random seed for reproducibility")
    parser.add_argument("--include-true-fact", action="store_true",
                       help="Include the true fact in context (makes it harder)")
    
    args = parser.parse_args()
    
    # Load knowledge graph
    print(f"Loading knowledge graph from {args.kg}...")
    g = Graph()
    g.parse(args.kg, format="turtle")
    print(f"Loaded {len(g)} triples")
    
    # Extract triples for predicate
    P = URIRef(args.pred)
    triples = get_triples(g, P)
    print(f"Found {len(triples)} triples for predicate {args.pred}")
    
    if len(triples) == 0:
        print("ERROR: No triples found for specified predicate")
        return
    
    # Extract unique subjects and objects
    subjects = list({s for s, _ in triples})
    objects = list({o for _, o in triples})
    triple_set = set(triples)
    
    # Initialize random generator
    rnd = random.Random(args.seed)
    
    cards = []
    attempts = 0
    max_attempts = args.num * 10
    
    print(f"\nGenerating {args.num} near-miss adversarial cards...")
    
    while len(cards) < args.num and attempts < max_attempts:
        attempts += 1
        
        # Pick a true triple
        s, o_true = rnd.choice(triples)
        
        # Pick a plausible but false object (different from true one)
        o_false_candidates = [x for x in objects if x != o_true and (s, x) not in triple_set]
        if not o_false_candidates:
            continue
        
        o_false = rnd.choice(o_false_candidates)
        
        # Construct context facts
        if args.include_true_fact:
            # Include the true fact to make it harder (tests if LLM can distinguish)
            facts = [
                format_fact(s, args.pred_label, o_true),
                f"(Testing: the following is FALSE)"
            ]
        else:
            # Just provide context about this subject
            facts = [format_fact(s, args.pred_label, o_true)]
        
        # Construct question about the false pairing
        question = format_question(s, args.pred_label, o_false)
        
        # Create card
        card = {
            "id": f"NEG_{len(cards):06d}",
            "facts": facts,
            "question": question,
            "gold": "NO",
            "label": "C",
            "claim": {"subj": s, "pred": args.pred, "obj": o_false}
        }
        
        cards.append(card)
        
        # Progress indicator
        if len(cards) % 100 == 0:
            print(f"Generated {len(cards)} cards...")
    
    # Write output
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    
    print(f"\n{'='*60}")
    print(f"Successfully generated {len(cards)} near-miss adversarial cards")
    print(f"Output: {args.out}")
    print(f"Attempts: {attempts}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()


