from rdflib import Graph
from pyshacl import validate

DATA_GRAPH_PATH = "data/knowledge_graph.ttl"
SHACL_GRAPH_PATH = "ontology/worldmind_constraints.shacl.ttl"


def validate_knowledge_graph():
    """Validates the data graph against the SHACL shapes."""
    try:
        data_graph = Graph().parse(DATA_GRAPH_PATH, format="turtle")
        shacl_graph = Graph().parse(SHACL_GRAPH_PATH, format="turtle")
    except FileNotFoundError as e:
        print(f"Error: Could not find a required file: {e}. Run 'make build' first.")
        return

    print("Running SHACL validation...")

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_graph, inference="rdfs", abort_on_first=False
    )

    print("\n--- Validation Report ---")
    if conforms:
        print("✅ Graph is conformant. No constraint violations found.")
    else:
        print("❌ Graph is NOT conformant. Violations found:")
        print(results_text)


if __name__ == "__main__":
    validate_knowledge_graph()
