import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD

INPUT_PATH = "data/raw_philosophers.csv"
OUTPUT_PATH = "data/knowledge_graph.ttl"
ONTOLOGY_PATH = "ontology/worldmind_core.ttl"

# Define namespaces
WM = Namespace("http://worldmind.ai/core#")


def create_knowledge_graph():
    """Builds the RDF graph from the raw CSV data."""
    try:
        df = pd.read_csv(INPUT_PATH)
    except FileNotFoundError:
        print(f"Error: Raw data file not found at {INPUT_PATH}. Run 'make data' first.")
        return

    g = Graph()
    g.parse(ONTOLOGY_PATH, format="turtle")  # Load our core ontology

    print(f"Processing {len(df)} records to build the knowledge graph...")

    for _, row in df.iterrows():
        person_uri = URIRef(row["person"])
        teacher_uri = URIRef(row["teacher"])

        # Add types
        g.add((person_uri, RDF.type, WM.Agent))
        g.add((teacher_uri, RDF.type, WM.Agent))

        # Add labels
        g.add((person_uri, RDFS.label, Literal(row["personLabel"], lang="en")))
        g.add((teacher_uri, RDFS.label, Literal(row["teacherLabel"], lang="en")))

        # Add temporal extents (lifespans)
        try:
            person_lifespan = URIRef(f"{person_uri}/timespan")
            g.add((person_uri, WM.hasTemporalExtent, person_lifespan))
            g.add((person_lifespan, RDF.type, WM.TimeSpan))
            g.add((person_lifespan, WM.start, Literal(row["personBirth"], datatype=XSD.date)))
            g.add((person_lifespan, WM.end, Literal(row["personDeath"], datatype=XSD.date)))
        except (ValueError, TypeError):
            pass  # Skip invalid dates

        try:
            teacher_lifespan = URIRef(f"{teacher_uri}/timespan")
            g.add((teacher_uri, WM.hasTemporalExtent, teacher_lifespan))
            g.add((teacher_lifespan, RDF.type, WM.TimeSpan))
            g.add((teacher_lifespan, WM.start, Literal(row["teacherBirth"], datatype=XSD.date)))
            g.add((teacher_lifespan, WM.end, Literal(row["teacherDeath"], datatype=XSD.date)))
        except (ValueError, TypeError):
            pass  # Skip invalid dates

        # Add the core relationship
        g.add((person_uri, WM.influencedBy, teacher_uri))

    g.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Knowledge graph built with {len(g)} triples and saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    create_knowledge_graph()
