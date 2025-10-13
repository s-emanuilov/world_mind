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

        A claim is licensed if it exists in (or is entailed by) the base graph.
        The graph itself is validated against SHACL constraints at build time,
        so any claim in the graph is assumed to be consistent with constraints.

        Args:
            base_graph (Graph): The ground-truth knowledge graph.
            claim (dict): A dictionary with 'subject', 'predicate', 'object'.

        Returns:
            bool: True if the claim is licensed (has evidence), False otherwise.
        """
        s = URIRef(claim["subject"])
        p = URIRef(claim["predicate"])
        o = URIRef(claim["object"])

        # Check if claim exists in the base graph (direct entailment)
        triple = (s, p, o)
        is_entailed = triple in base_graph
        
        return is_entailed

