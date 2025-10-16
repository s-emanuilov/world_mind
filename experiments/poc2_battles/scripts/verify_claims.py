"""
Verify extracted claims against the knowledge graph using the existing auditor + policy.
Outputs a concise JSON summary and per-claim results.
"""

import json
import os
import sys
import argparse
from typing import Dict, Any

# Import worldmind components
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from worldmind import GraphStore, ConsistencyAuditor, AbstentionPolicy


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

CLAIMS_IN_DEFAULT = os.path.join(EXPERIMENT_DIR, "artifacts", "llm_claims.jsonl")
RESULTS_OUT_DEFAULT = os.path.join(EXPERIMENT_DIR, "artifacts", "llm_eval.json")

GRAPH_PATH = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")
CONSTRAINTS_PATH = os.path.join(EXPERIMENT_DIR, "ontology", "worldmind_constraints.shacl.ttl")


def normalize_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure string or None
    return {
        "subject": claim.get("subject") if claim.get("subject") else None,
        "predicate": claim.get("predicate") if claim.get("predicate") else None,
        "object": claim.get("object") if claim.get("object") else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims", type=str, default=CLAIMS_IN_DEFAULT)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    claims_path = args.claims
    results_out = args.out or (
        os.path.join(
            EXPERIMENT_DIR,
            "artifacts",
            f"llm_eval_{os.path.splitext(os.path.basename(claims_path))[0].replace('.', '_')}.json",
        )
    )

    store = GraphStore(GRAPH_PATH)
    auditor = ConsistencyAuditor(CONSTRAINTS_PATH)
    policy = AbstentionPolicy()
    base_graph = store.get_graph()

    results = []
    passed = 0
    total = 0

    with open(claims_path, "r") as inf:
        for line in inf:
            total += 1
            rec = json.loads(line)
            claim = normalize_claim(rec.get("claim", {}))

            is_licensed = False
            if claim["subject"] and claim["predicate"] and claim["object"]:
                is_licensed = auditor.audit_claim(base_graph, claim)

            decision = policy.decide(is_licensed)
            # There is no ground-truth here, just report decision and license
            results.append({
                "id": rec.get("id"),
                "claim": claim,
                "licensed": is_licensed,
                "decision": decision,
            })

    summary = {
        "total": total,
        "licensed": sum(1 for r in results if r["licensed"]),
        "answered": sum(1 for r in results if r["decision"] == "ANSWER"),
        "abstained": sum(1 for r in results if r["decision"] == "ABSTAIN"),
    }

    os.makedirs(os.path.dirname(results_out), exist_ok=True)
    with open(results_out, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Results saved to {results_out}")


if __name__ == "__main__":
    main()


