import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
import os

# Determine paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

INPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "raw_battles.csv")
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")
ONTOLOGY_PATH = os.path.join(EXPERIMENT_DIR, "ontology", "worldmind_core.ttl")

# Define namespaces
WM = Namespace("http://worldmind.ai/battles#")


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

    # Track entities to avoid duplicate processing
    battles_seen = set()
    commanders_seen = set()
    countries_seen = set()

    for _, row in df.iterrows():
        battle_uri = URIRef(row["battle"])
        commander_uri = URIRef(row["commander"])
        
        # Add battle (only once per unique battle)
        if battle_uri not in battles_seen:
            g.add((battle_uri, RDF.type, WM.Battle))
            g.add((battle_uri, RDFS.label, Literal(row["battleLabel"], lang="en")))
            
            # Add battle date
            try:
                g.add((battle_uri, WM.occurredOn, Literal(row["battleDate"], datatype=XSD.date)))
            except (ValueError, TypeError):
                pass  # Skip invalid dates
            
            battles_seen.add(battle_uri)

        # Add commander to battle relationship
        g.add((battle_uri, WM.hasCommander, commander_uri))

        # Add commander (only once per unique commander)
        if commander_uri not in commanders_seen:
            g.add((commander_uri, RDF.type, WM.Agent))
            g.add((commander_uri, RDFS.label, Literal(row["commanderLabel"], lang="en")))

            # Add commander's lifespan
            try:
                lifespan_uri = URIRef(f"{commander_uri}/timespan")
                g.add((commander_uri, WM.hasTemporalExtent, lifespan_uri))
                g.add((lifespan_uri, RDF.type, WM.TimeSpan))
                g.add((lifespan_uri, WM.start, Literal(row["commanderBirth"], datatype=XSD.date)))
                g.add((lifespan_uri, WM.end, Literal(row["commanderDeath"], datatype=XSD.date)))
            except (ValueError, TypeError):
                pass  # Skip invalid dates

            commanders_seen.add(commander_uri)

        # Add country if present
        if pd.notna(row.get("country")):
            country_uri = URIRef(row["country"])
            
            # Add country type and label (only once)
            if country_uri not in countries_seen:
                g.add((country_uri, RDF.type, WM.Country))
                if pd.notna(row.get("countryLabel")):
                    g.add((country_uri, RDFS.label, Literal(row["countryLabel"], lang="en")))
                countries_seen.add(country_uri)
            
            # Link commander to their nationality
            g.add((commander_uri, WM.hasNationality, country_uri))
            
            # Link battle to combatant country
            g.add((battle_uri, WM.hasCombatant, country_uri))

    g.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Knowledge graph built with {len(g)} triples and saved to {OUTPUT_PATH}")
    print(f"  - {len(battles_seen)} unique battles")
    print(f"  - {len(commanders_seen)} unique commanders")
    print(f"  - {len(countries_seen)} unique countries")


if __name__ == "__main__":
    create_knowledge_graph()

