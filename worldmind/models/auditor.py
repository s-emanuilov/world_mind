from rdflib import Graph, URIRef, Namespace
from pyshacl import validate


class ConsistencyAuditor:
    """
    Acts as the 'Licensing Oracle' by validating claims against a knowledge graph
    using a set of SHACL constraints.
    """

    def __init__(self, shacl_graph_path: str):
        """
        Initializes the auditor with the SHACL constraints graph.

        Args:
            shacl_graph_path (str): Path to the Turtle file with SHACL shapes.
        """
        self.shacl_graph = Graph().parse(shacl_graph_path, format="turtle")
        print("Consistency Auditor initialized with SHACL constraints.")

    def audit_claim(self, base_graph: Graph, claim: dict) -> bool:
        """
        Audits a single claim against the base knowledge graph.

        This method works by creating a temporary copy of the graph, adding the
        hypothetical claim to it, and then running SHACL validation. This ensures
        the base graph remains unchanged.

        Args:
            base_graph (Graph): The ground-truth knowledge graph.
            claim (dict): A dictionary with 'subject', 'predicate', 'object'.

        Returns:
            bool: True if the claim is licensed (conforms to shapes), False otherwise.
        """
        # Create a temporary graph with the base data + the new claim
        temp_graph = Graph()
        temp_graph += base_graph

        # Define a namespace for our ontology for cleaner triple creation
        WM = Namespace("http://worldmind.ai/core#")

        s = URIRef(claim["subject"])
        p = URIRef(claim["predicate"])
        o = URIRef(claim["object"])

        temp_graph.add((s, p, o))

        # Run the validation
        conforms, _, _ = validate(
            temp_graph,
            shacl_graph=self.shacl_graph,
            inference="rdfs",
            abort_on_first=True,  # Stop as soon as one violation is found for efficiency
        )

        return conforms

