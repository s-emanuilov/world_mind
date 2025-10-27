#!/usr/bin/env python3
"""
Validate knowledge graph against SHACL constraints.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

try:
    import pyshacl
    PYSHACL_AVAILABLE = True
except ImportError:
    PYSHACL_AVAILABLE = False
    print("WARNING: pyshacl not available")


def validate_graph(graph_path: str, ontology_path: str, constraints_path: str):
    """Validate graph against SHACL constraints."""
    if not PYSHACL_AVAILABLE:
        print("ERROR: pyshacl not available")
        return False
    
    print(f"Validating {graph_path} against {constraints_path}...")
    
    try:
        r = pyshacl.validate(
            shacl_graph=constraints_path,
            ont_graph=ontology_path,
            data_graph=graph_path,
            ontologies_graph=ontology_path,
            inference='rdfs'
        )
        
        conforms, results_graph, results_text = r
        
        if conforms:
            print("✓ Graph passes all SHACL constraints!")
            return True
        else:
            print("✗ Graph has constraint violations:")
            print(results_text)
            return False
            
    except Exception as e:
        print(f"ERROR during validation: {e}")
        return False


def main():
    graph_path = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")
    ontology_path = os.path.join(EXPERIMENT_DIR, "ontology", "worldmind_core.ttl")
    constraints_path = os.path.join(EXPERIMENT_DIR, "ontology", "worldmind_constraints.shacl.ttl")
    
    if not os.path.exists(graph_path):
        print(f"ERROR: Graph file not found: {graph_path}")
        print("Run 'make data' first to build the graph")
        sys.exit(1)
    
    if not os.path.exists(constraints_path):
        print(f"ERROR: Constraints file not found: {constraints_path}")
        sys.exit(1)
    
    success = validate_graph(graph_path, ontology_path, constraints_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
