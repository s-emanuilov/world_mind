from rdflib import Graph
import os


class GraphStore:
    """Manages loading and accessing the knowledge graph."""

    def __init__(self, graph_path: str):
        if not os.path.exists(graph_path):
            raise FileNotFoundError(
                f"Knowledge graph file not found at {graph_path}. Please run 'make build'."
            )

        print(f"Loading knowledge graph from {graph_path}...")
        self.graph = Graph()
        self.graph.parse(graph_path, format="turtle")
        print(f"Graph loaded with {len(self.graph)} triples.")

    def get_graph(self) -> Graph:
        """Returns the loaded RDF graph."""
        return self.graph

