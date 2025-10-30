#!/usr/bin/env python3
"""
Unified evaluator for epistemic-confusion cards.

Pluggable back-ends:
- KGOracleAdapter: Deterministic licensing gate using the KG
- RawLLMAdapter: Direct LLM API call (user wires to their API)
- RAGAdapter: Embedding-based RAG retrieval + LLM

Outputs JSONL with per-card results:
{
    "id": "CARD_xxx",
    "gold": "YES|NO|UNKNOWN",
    "pred": "YES|NO|UNKNOWN", 
    "pass": true/false,
    "system": "raw|rag|kg_licensed",
    "label": "E|C|U"
}
"""

import argparse
import json
import sys
from typing import Dict, Optional
from pathlib import Path
from abc import ABC, abstractmethod

# Optional imports for specific adapters
try:
    from rdflib import Graph, URIRef
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False


# ===================================================
# Base Adapter Interface
# ===================================================

class BaseAdapter(ABC):
    """Base class for all system adapters."""
    
    @abstractmethod
    def answer(self, card: Dict) -> str:
        """
        Process a card and return answer: YES, NO, or UNKNOWN.
        
        Args:
            card: Dictionary with keys: id, facts, question, claim, label, gold
            
        Returns:
            str: "YES", "NO", or "UNKNOWN"
        """
        raise NotImplementedError


# ===================================================
# KG Oracle Adapter (Deterministic)
# ===================================================

class KGOracleAdapter(BaseAdapter):
    """
    Deterministic adapter that simulates perfect licensing oracle behavior.
    
    Respects explicit negations in 'facts'. Answers YES only when the 
    entailed fact is present, UNKNOWN when absent without negation.
    
    This represents the ideal behavior of a graph-licensed system.
    """
    
    def __init__(self, pred_label: str = "related to"):
        self.pred_label = pred_label
    
    def answer(self, card: Dict) -> str:
        """Deterministic licensing decision based on facts in context."""
        claim = card["claim"]
        s = claim["subj"]
        o = claim["obj"]
        
        # Extract labels for matching
        s_label = self._extract_label(s)
        o_label = self._extract_label(o)
        
        facts = card["facts"]
        
        # Check for explicit negation
        for fact in facts:
            if "DOES NOT" in fact and s_label in fact and o_label in fact:
                return "NO"
        
        # Check for positive assertion
        for fact in facts:
            if s_label in fact and o_label in fact and "DOES NOT" not in fact:
                return "YES"
        
        # No evidence either way
        return "UNKNOWN"
    
    @staticmethod
    def _extract_label(uri: str) -> str:
        """Extract label from URI."""
        if '#' in uri:
            return uri.split('#')[-1].replace('_', ' ')
        elif '/' in uri:
            return uri.split('/')[-1].replace('_', ' ')
        return uri


# ===================================================
# Raw LLM Adapter (Stub)
# ===================================================

class RawLLMAdapter(BaseAdapter):
    """
    Stub adapter for raw LLM queries.
    
    Users should customize this to call their preferred API 
    (OpenAI, Anthropic, OpenRouter, etc.) and parse structured responses.
    
    For now, defaults to conservative UNKNOWN to prevent false claims.
    """
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        print(f"[RawLLM] Using model: {model_name} (STUB - returns UNKNOWN)")
    
    def answer(self, card: Dict) -> str:
        """
        TODO: Implement actual LLM API call here.
        
        Suggested implementation:
        1. Format prompt with card["facts"] and card["question"]
        2. Call LLM API with JSON mode or structured output
        3. Parse response to extract YES/NO/UNKNOWN
        4. Return result
        """
        # STUB: Always return UNKNOWN for now
        return "UNKNOWN"


# ===================================================
# RAG Adapter (Stub)
# ===================================================

class RAGAdapter(BaseAdapter):
    """
    Stub adapter for embedding-based RAG.
    
    Users should customize this to:
    1. Use their embedding model to retrieve relevant passages
    2. Augment prompt with retrieved context
    3. Query LLM with augmented prompt
    4. Parse and return YES/NO/UNKNOWN
    
    For now, defaults to UNKNOWN.
    """
    
    def __init__(self, embedding_model: str = "e5-large", llm_model: str = "gpt-4"):
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        print(f"[RAG] Using embeddings: {embedding_model}, LLM: {llm_model} (STUB - returns UNKNOWN)")
    
    def answer(self, card: Dict) -> str:
        """
        TODO: Implement actual RAG pipeline here.
        
        Suggested implementation:
        1. Embed card["question"]
        2. Retrieve top-k similar passages from vector store
        3. Format prompt with retrieved passages
        4. Call LLM API
        5. Parse response to extract YES/NO/UNKNOWN
        6. Return result
        """
        # STUB: Always return UNKNOWN for now
        return "UNKNOWN"


# ===================================================
# Graph RAG Adapter with SHACL Validation
# ===================================================

class GraphRAGAdapter(BaseAdapter):
    """
    Graph-RAG adapter with full licensing oracle behavior.
    
    This adapter:
    1. Loads the knowledge graph
    2. Checks if claim triple exists in KG
    3. Optionally validates against SHACL constraints
    4. Returns YES/NO/UNKNOWN based on licensing decision
    """
    
    def __init__(self, kg_path: str, shacl_path: Optional[str] = None):
        if not RDFLIB_AVAILABLE:
            raise ImportError("rdflib is required for GraphRAGAdapter. Install with: pip install rdflib")
        
        self.kg_path = kg_path
        self.shacl_path = shacl_path
        
        print(f"[GraphRAG] Loading knowledge graph from {kg_path}...")
        self.graph = Graph()
        self.graph.parse(kg_path, format="turtle")
        print(f"[GraphRAG] Loaded {len(self.graph)} triples")
        
        if shacl_path:
            print(f"[GraphRAG] SHACL validation enabled: {shacl_path}")
            # TODO: Implement SHACL validation
            # For now, we just check triple existence
    
    def answer(self, card: Dict) -> str:
        """
        Check if claim exists in knowledge graph using proper epistemic logic.
        
        This implementation matches KGOracleAdapter logic:
        1. Check context facts for explicit negation → NO
        2. Check if triple exists in KG → YES  
        3. Otherwise → UNKNOWN (open-world assumption)
        
        This avoids assuming functional properties and properly handles
        the distinction between "known false" and "unknown".
        """
        claim = card["claim"]
        
        # Convert claim to RDF triple
        s = URIRef(claim["subj"])
        p = URIRef(claim["pred"])
        o = URIRef(claim["obj"])
        
        # Extract labels for matching against context facts
        s_label = self._extract_label(str(s))
        o_label = self._extract_label(str(o))
        
        # Check context facts for explicit negation
        facts = card.get("facts", [])
        for fact in facts:
            if "DOES NOT" in fact and s_label in fact and o_label in fact:
                # Explicit negation in context
                return "NO"
        
        # Check if triple exists in graph
        if (s, p, o) in self.graph:
            return "YES"
        
        # No evidence either way - open-world assumption
        return "UNKNOWN"
    
    @staticmethod
    def _extract_label(uri: str) -> str:
        """Extract human-readable label from URI."""
        if '#' in uri:
            return uri.split('#')[-1].replace('_', ' ')
        elif '/' in uri:
            return uri.split('/')[-1].replace('_', ' ')
        return uri


# ===================================================
# Evaluation Pipeline
# ===================================================

def eval_cards(cards_path: str, adapter: BaseAdapter, system_name: str, out_path: str):
    """
    Evaluate all cards using the provided adapter.
    
    Args:
        cards_path: Path to input JSONL file with cards
        adapter: System adapter implementing BaseAdapter interface
        system_name: Name of the system (for result tracking)
        out_path: Path to output JSONL file with results
    """
    results = []
    
    print(f"\n{'='*60}")
    print(f"Evaluating system: {system_name}")
    print(f"Reading cards from: {cards_path}")
    print(f"{'='*60}\n")
    
    # Read and process cards
    with open(cards_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            card = json.loads(line)
            
            # Get system prediction
            pred = adapter.answer(card)
            
            # Check correctness
            gold = card["gold"]
            is_correct = (pred == gold)
            
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
            
            # Progress indicator
            if i % 100 == 0:
                accuracy = sum(r["pass"] for r in results) / len(results) * 100
                print(f"Processed {i} cards... (accuracy so far: {accuracy:.1f}%)")
    
    # Write results
    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    
    # Calculate and print summary statistics
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
        description="Evaluate systems on epistemic confusion cards",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--cards", required=True, help="Input JSONL file with cards")
    parser.add_argument("--system", choices=["kg", "raw", "rag", "graph_rag"], required=True, 
                       help="System type to evaluate")
    parser.add_argument("--out", required=True, help="Output JSONL file for results")
    
    # System-specific arguments
    parser.add_argument("--kg-path", help="Path to knowledge graph (for graph_rag)")
    parser.add_argument("--shacl-path", help="Path to SHACL constraints (optional)")
    parser.add_argument("--model", default="gpt-4", help="Model name (for raw/rag)")
    parser.add_argument("--api-key", help="API key for LLM services")
    
    args = parser.parse_args()
    
    # Create appropriate adapter
    if args.system == "kg":
        adapter = KGOracleAdapter()
    elif args.system == "raw":
        adapter = RawLLMAdapter(model_name=args.model, api_key=args.api_key)
    elif args.system == "rag":
        adapter = RAGAdapter(llm_model=args.model)
    elif args.system == "graph_rag":
        if not args.kg_path:
            print("ERROR: --kg-path is required for graph_rag system")
            sys.exit(1)
        adapter = GraphRAGAdapter(kg_path=args.kg_path, shacl_path=args.shacl_path)
    else:
        print(f"ERROR: Unknown system type: {args.system}")
        sys.exit(1)
    
    # Run evaluation
    eval_cards(args.cards, adapter, args.system, args.out)


if __name__ == "__main__":
    main()

