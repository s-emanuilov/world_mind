#!/usr/bin/env python3
"""
Generate "context cards" from a KG TTL for epistemic-confusion tests.

Card schema (JSONL):
{
    "id": "CARD_0001",
    "facts": ["Escanaba River has mouth: Lake Michigan", "...", "Bear Creek DOES NOT have tributary: Whetstone River"],
    "question": "Is Whetstone River a tributary of Bear Creek?",
    "gold": "YES|NO|UNKNOWN",
    "claim": {"subj":"IRI","pred":"IRI","obj":"IRI"},
    "label": "E|C|U"  # entailed / contradictory / unknown
}

Label meanings:
- E (Entailed): Triple is in the KG or logically entailed
- C (Contradictory): Violates a SHACL constraint or explicitly negated
- U (Unknown): Not present and not provably contradictory (open-world)
"""

import argparse
import json
import random
from typing import List, Tuple, Set
from pathlib import Path
from rdflib import Graph, URIRef, Namespace


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


def make_card(card_id: str, facts: List[str], question: str, gold: str, label: str, claim: dict) -> dict:
    """Create a context card with all required fields."""
    return {
        "id": card_id,
        "facts": facts,
        "question": question,
        "gold": gold,  # YES/NO/UNKNOWN
        "label": label,  # E/C/U
        "claim": claim
    }


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
        description="Generate epistemic confusion test cards from knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--kg", required=True, help="Path to TTL knowledge graph")
    parser.add_argument("--pred", required=True, help="Predicate IRI (e.g., http://worldmind.ai/rivers-v4#hasMouth)")
    parser.add_argument("--pred-label", default="related to", help="Human-readable predicate label")
    parser.add_argument("--subj-hint", default=None, help="Optional substring to filter subjects")
    parser.add_argument("--num-per-type", type=int, default=200, help="Number of cards per type (E/C/U)")
    parser.add_argument("--out", required=True, help="Output JSONL file path")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Load knowledge graph
    print(f"Loading knowledge graph from {args.kg}...")
    g = Graph()
    g.parse(args.kg, format="turtle")
    print(f"Loaded {len(g)} triples")
    
    # Extract triples for the specified predicate
    pred_uri = URIRef(args.pred)
    triples = get_triples(g, pred_uri)
    
    # Filter by subject hint if provided
    if args.subj_hint:
        triples = [(s, o) for s, o in triples if args.subj_hint in s]
    
    print(f"Found {len(triples)} triples for predicate {args.pred}")
    
    if len(triples) == 0:
        print("ERROR: No triples found for specified predicate. Check the predicate URI.")
        return
    
    # Extract unique subjects and objects
    subjects = list({s for s, _ in triples})
    objects = list({o for _, o in triples})
    triple_set = set(triples)
    
    # Initialize random generator for reproducibility
    rnd = random.Random(args.seed)
    cards = []
    
    # ========================================
    # 1) Entailed TRUE (E) -> gold YES
    # ========================================
    print(f"\nGenerating {args.num_per_type} ENTAILED (E) cards...")
    for _ in range(min(args.num_per_type, len(triples))):
        s, o = rnd.choice(triples)
        facts = [format_fact(s, args.pred_label, o)]
        question = format_question(s, args.pred_label, o)
        
        cards.append(make_card(
            card_id=f"CARD_E_{len(cards):06d}",
            facts=facts,
            question=question,
            gold="YES",
            label="E",
            claim={"subj": s, "pred": args.pred, "obj": o}
        ))
    
    # ========================================
    # 2) Explicitly FALSE (C) -> gold NO
    # ========================================
    print(f"Generating {args.num_per_type} CONTRADICTORY (C) cards...")
    for _ in range(min(args.num_per_type, len(triples))):
        s, o_true = rnd.choice(triples)
        # Choose a false object (different from true one)
        o_false_candidates = [x for x in objects if x != o_true]
        if not o_false_candidates:
            continue
        o_false = rnd.choice(o_false_candidates)
        
        # Provide context with true fact and explicit negation
        facts = [
            format_fact(s, args.pred_label, o_true),
            f"{extract_label(s)} DOES NOT have {args.pred_label}: {extract_label(o_false)} (not in database)"
        ]
        question = format_question(s, args.pred_label, o_false)
        
        cards.append(make_card(
            card_id=f"CARD_C_{len(cards):06d}",
            facts=facts,
            question=question,
            gold="NO",
            label="C",
            claim={"subj": s, "pred": args.pred, "obj": o_false}
        ))
    
    # ========================================
    # 3) UNKNOWN (U) -> gold UNKNOWN
    # ========================================
    print(f"Generating {args.num_per_type} UNKNOWN (U) cards...")
    attempts = 0
    max_attempts = args.num_per_type * 10  # Prevent infinite loop
    
    while len([c for c in cards if c["label"] == "U"]) < args.num_per_type and attempts < max_attempts:
        attempts += 1
        s, _ = rnd.choice(triples)
        
        # Find objects NOT in triples for this subject
        o_candidates = [x for x in objects if (s, x) not in triple_set]
        if not o_candidates:
            continue
        
        o = rnd.choice(o_candidates)
        
        # Provide context with OTHER known facts for this subject (no explicit negation)
        subject_facts = [format_fact(s2, args.pred_label, o2) 
                        for s2, o2 in triples if s2 == s]
        
        if not subject_facts:
            continue
        
        # Only include some facts, not all (simulate incomplete context)
        facts = rnd.sample(subject_facts, min(3, len(subject_facts)))
        question = format_question(s, args.pred_label, o)
        
        cards.append(make_card(
            card_id=f"CARD_U_{len(cards):06d}",
            facts=facts,
            question=question,
            gold="UNKNOWN",
            label="U",
            claim={"subj": s, "pred": args.pred, "obj": o}
        ))
    
    # ========================================
    # 4) Distractor/Coherence traps (C) -> gold NO
    # ========================================
    print(f"Generating {args.num_per_type} DISTRACTOR (C) cards...")
    for _ in range(args.num_per_type):
        if len(triples) < 2:
            break
        
        # Mix facts from two different subjects to create coherent but false combination
        s1, o1 = rnd.choice(triples)
        s2, o2 = rnd.choice(triples)
        
        if s1 == s2:
            continue
        
        # Provide true facts for both, then ask about wrong pairing (s1, o2)
        if (s1, o2) in triple_set:
            continue  # Skip if this happens to be true
        
        facts = [
            format_fact(s1, args.pred_label, o1),
            format_fact(s2, args.pred_label, o2)
        ]
        question = format_question(s1, args.pred_label, o2)
        
        cards.append(make_card(
            card_id=f"CARD_D_{len(cards):06d}",
            facts=facts,
            question=question,
            gold="NO",
            label="C",
            claim={"subj": s1, "pred": args.pred, "obj": o2}
        ))
    
    # Write cards to JSONL file
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    
    # Print summary statistics
    label_counts = {}
    for card in cards:
        label = card["label"]
        label_counts[label] = label_counts.get(label, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"Successfully generated {len(cards)} context cards")
    print(f"Output: {args.out}")
    print(f"\nBreakdown by label:")
    for label, count in sorted(label_counts.items()):
        label_name = {"E": "Entailed", "C": "Contradictory", "U": "Unknown"}[label]
        print(f"  {label} ({label_name}): {count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()


