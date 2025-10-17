import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
import os

# Determine paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

INPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "raw_rivers.csv")
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")
ONTOLOGY_PATH = os.path.join(EXPERIMENT_DIR, "ontology", "worldmind_core.ttl")

# Define namespaces
WM = Namespace("http://worldmind.ai/rivers#")


def create_knowledge_graph():
    """Builds the RDF graph of US rivers from the raw CSV data."""
    try:
        df = pd.read_csv(INPUT_PATH)
    except FileNotFoundError:
        print(f"Error: Raw data file not found at {INPUT_PATH}. Run 'make data' first.")
        return

    g = Graph()
    g.parse(ONTOLOGY_PATH, format="turtle")  # Load our core ontology

    print(f"Processing {len(df)} records to build the knowledge graph...")

    # Track entities to avoid duplicate processing
    rivers_seen = set()
    places_seen = set()

    def is_uri(value: str) -> bool:
        if not isinstance(value, str):
            return False
        return value.startswith("http://") or value.startswith("https://")

    def ref_or_literal(value):
        try:
            if is_uri(value):
                return URIRef(value)
            return Literal(value)
        except Exception:
            return Literal(str(value))

    for _, row in df.iterrows():
        if pd.isna(row.get("river")):
            continue
        river_uri = URIRef(row["river"]) 

        # Add river (only once per unique river)
        if river_uri not in rivers_seen:
            g.add((river_uri, RDF.type, WM.River))
            if pd.notna(row.get("riverLabel")):
                g.add((river_uri, RDFS.label, Literal(row["riverLabel"], lang="en")))
            # physical attributes
            if pd.notna(row.get("length")):
                try:
                    g.add((river_uri, WM.length, Literal(float(row["length"]), datatype=XSD.double)))
                except Exception:
                    pass
            if pd.notna(row.get("discharge")):
                try:
                    g.add((river_uri, WM.discharge, Literal(float(row["discharge"]), datatype=XSD.double)))
                except Exception:
                    pass
            if pd.notna(row.get("basin")):
                try:
                    g.add((river_uri, WM.drainageBasin, URIRef(row["basin"])))
                except Exception:
                    pass
            rivers_seen.add(river_uri)

        # country (US)
        if pd.notna(row.get("country")):
            country_obj = ref_or_literal(row["country"])
            g.add((river_uri, WM.inCountry, country_obj))

        # states traversed
        if pd.notna(row.get("state")):
            g.add((river_uri, WM.traverses, ref_or_literal(row["state"])) )

        # source feature
        if pd.notna(row.get("source")):
            source_obj = ref_or_literal(row["source"]) 
            g.add((river_uri, WM.hasSource, source_obj))
            if isinstance(source_obj, URIRef) and source_obj not in places_seen:
                g.add((source_obj, RDF.type, WM.GeographicFeature))
                if pd.notna(row.get("sourceLabel")):
                    g.add((source_obj, RDFS.label, Literal(row["sourceLabel"], lang="en")))
                if pd.notna(row.get("sourceElevation")):
                    try:
                        g.add((source_obj, WM.elevation, Literal(float(row["sourceElevation"]), datatype=XSD.double)))
                    except Exception:
                        pass
                places_seen.add(source_obj)

        # mouth feature
        if pd.notna(row.get("mouth")):
            mouth_obj = ref_or_literal(row["mouth"]) 
            g.add((river_uri, WM.hasMouth, mouth_obj))
            if isinstance(mouth_obj, URIRef) and mouth_obj not in places_seen:
                g.add((mouth_obj, RDF.type, WM.GeographicFeature))
                if pd.notna(row.get("mouthLabel")):
                    g.add((mouth_obj, RDFS.label, Literal(row["mouthLabel"], lang="en")))
                places_seen.add(mouth_obj)

        # tributaries
        if pd.notna(row.get("tributary")):
            g.add((river_uri, WM.hasTributary, ref_or_literal(row["tributary"])) )

    g.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Knowledge graph built with {len(g)} triples and saved to {OUTPUT_PATH}")
    print(f"  - {len(rivers_seen)} unique rivers")
    print(f"  - {len(places_seen)} unique geographic features")


if __name__ == "__main__":
    create_knowledge_graph()

