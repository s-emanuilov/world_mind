#!/usr/bin/env python3
"""
Build knowledge graph from rivers CSV data.
Converts CSV rows to RDF triples using the worldmind ontology.
"""

import csv
import os
import re
import sys
from typing import Dict, Any, List
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD

# Add project root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(EXPERIMENT_DIR)))

sys.path.insert(0, PROJECT_ROOT)

# Namespaces
WM = Namespace("http://worldmind.ai/rivers-v4#")
DBR = Namespace("http://dbpedia.org/resource/")

def parse_length(length_str: str) -> float:
    """Parse length string to meters (convert mi to m)."""
    if not length_str or length_str.strip() == '':
        return None
    
    # Extract number - must have at least one digit
    match = re.search(r'(\d+\.?\d*)', length_str)
    if not match:
        return None
    
    try:
        num = float(match.group())
    except ValueError:
        return None
    
    # Check unit
    if 'mi' in length_str.lower() or 'mile' in length_str.lower():
        return num * 1609.34  # Convert miles to meters
    elif 'km' in length_str.lower() or 'kilometer' in length_str.lower():
        return num * 1000
    else:
        return num  # assume meters
    
def parse_elevation(elev_str: str) -> float:
    """Parse elevation string to meters."""
    if not elev_str or elev_str.strip() == '':
        return None
    
    # Extract number - must have at least one digit
    match = re.search(r'(\d+\.?\d*)', elev_str)
    if not match:
        return None
    
    try:
        num = float(match.group())
    except ValueError:
        return None
    
    # Check unit
    if 'feet' in elev_str.lower() or 'ft' in elev_str.lower():
        return num * 0.3048  # Convert feet to meters
    elif 'meter' in elev_str.lower() or 'm' in elev_str.lower() or 'metre' in elev_str.lower():
        return num
    else:
        return num
    
def parse_discharge(discharge_str: str) -> float:
    """Parse discharge to m³/s."""
    if not discharge_str or discharge_str.strip() == '':
        return None
    
    # Extract number - must have at least one digit
    match = re.search(r'(\d+\.?\d*)', discharge_str)
    if not match:
        return None
    
    try:
        num = float(match.group())
    except ValueError:
        return None
    
    # For now, assume it's already in m³/s if present
    # (many entries are ranges like "50 to 200 cubic feet per second")
    return num

def clean_uri_part(name: str) -> str:
    """Clean a name to make it URI-safe."""
    if not name:
        return name
    
    # Remove quotes, commas, arrows, parentheses and other problematic chars
    cleaned = name.replace('"', '').replace(',', '').replace('->', '_').replace('(', '').replace(')', '').replace(':', '_').replace(';', '_')
    # Replace spaces with underscores
    cleaned = cleaned.replace(' ', '_')
    # Remove multiple consecutive underscores
    while '__' in cleaned:
        cleaned = cleaned.replace('__', '_')
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    return cleaned

def add_river_triples(g: Graph, row: Dict[str, Any]) -> None:
    """Add triples for a river to the graph."""
    
    river_uri = URIRef(row['river'])
    g.add((river_uri, RDF.type, WM.River))
    g.add((river_uri, RDFS.label, Literal(row['riverName'])))
    
    # Add abstract if present
    if row.get('abstract'):
        g.add((river_uri, WM.abstractText, Literal(row['abstract'])))
    
    # Add other names
    if row.get('otherNames'):
        g.add((river_uri, WM.otherNames, Literal(row['otherNames'])))
    
    # Add length
    if row.get('length'):
        length = parse_length(row['length'])
        if length:
            g.add((river_uri, WM.length, Literal(length, datatype=XSD.double)))
    
    # Add discharge
    if row.get('discharge'):
        discharge = parse_discharge(row['discharge'])
        if discharge:
            g.add((river_uri, WM.discharge, Literal(discharge, datatype=XSD.double)))
    
    # Add source elevation
    if row.get('sourceElevation'):
        src_elev = parse_elevation(row['sourceElevation'])
        if src_elev:
            g.add((river_uri, WM.sourceElevation, Literal(src_elev, datatype=XSD.double)))
    
    # Add mouth elevation
    if row.get('mouthElevation'):
        mouth_elev = parse_elevation(row['mouthElevation'])
        if mouth_elev:
            g.add((river_uri, WM.mouthElevation, Literal(mouth_elev, datatype=XSD.double)))
    
    # Add country
    if row.get('country'):
        country_name = clean_uri_part(row['country'])
        country_uri = URIRef(DBR[country_name])
        g.add((country_uri, RDF.type, WM.Country))
        g.add((river_uri, WM.inCountry, country_uri))
    
    # Add states
    if row.get('state'):
        states = row['state'].split(';')
        for state_str in states:
            state_str = state_str.strip()
            if state_str:
                state_uri = URIRef(DBR[clean_uri_part(state_str)])
                g.add((state_uri, RDF.type, WM.State))
                g.add((river_uri, WM.traverses, state_uri))
    
    # Add counties
    if row.get('county'):
        counties = row['county'].split(';')
        for county_str in counties:
            county_str = county_str.strip()
            if county_str:
                county_uri = URIRef(DBR[clean_uri_part(county_str)])
                g.add((county_uri, RDF.type, WM.County))
                g.add((river_uri, WM.inCounty, county_uri))
    
    # Add river system
    if row.get('riverSystem'):
        sys_name = clean_uri_part(row['riverSystem'])
        sys_uri = URIRef(DBR[sys_name])
        g.add((sys_uri, RDF.type, WM.RiverSystem))
        g.add((river_uri, WM.partOfSystem, sys_uri))
    
    # Add source location (GeographicFeature)
    if row.get('sourceLocation'):
        source_name = clean_uri_part(row['sourceLocation'])
        source_uri = URIRef(DBR[source_name])
        g.add((source_uri, RDF.type, WM.GeographicFeature))
        g.add((source_uri, RDFS.label, Literal(row['sourceLocation'])))
        g.add((river_uri, WM.hasSource, source_uri))
        
        # Add source elevation to the feature
        if row.get('sourceElevation'):
            src_elev = parse_elevation(row['sourceElevation'])
            if src_elev:
                g.add((source_uri, WM.elevation, Literal(src_elev, datatype=XSD.double)))
    
    # Add mouth location
    if row.get('riverMouth'):
        mouth_name = clean_uri_part(row['riverMouth'])
        mouth_uri = URIRef(DBR[mouth_name])
        g.add((mouth_uri, RDF.type, WM.GeographicFeature))
        if row.get('mouthLocation'):
            g.add((mouth_uri, RDFS.label, Literal(row['mouthLocation'])))
        g.add((river_uri, WM.hasMouth, mouth_uri))
    
    # Add tributaries
    for prefix in ['leftTributary', 'rightTributary']:
        if row.get(prefix):
            # Tributary may be a URI or a name
            tributary_name = row[prefix]
            if not tributary_name.startswith('http://'):
                tributary_name = DBR[clean_uri_part(tributary_name)]
            tributary_uri = URIRef(tributary_name)
            g.add((tributary_uri, RDF.type, WM.River))
            g.add((river_uri, WM.hasTributary, tributary_uri))

def main():
    data_dir = os.path.join(os.path.dirname(EXPERIMENT_DIR), "data")
    input_csv = os.path.join(data_dir, "raw_rivers_filled.csv")
    
    if not os.path.exists(input_csv):
        print(f"ERROR: Input file not found: {input_csv}")
        sys.exit(1)
    
    graph_dir = os.path.join(EXPERIMENT_DIR, "data")
    os.makedirs(graph_dir, exist_ok=True)
    output_ttl = os.path.join(graph_dir, "knowledge_graph.ttl")
    
    g = Graph()
    g.bind("wm", WM)
    g.bind("dbr", DBR)
    
    print(f"Loading data from {input_csv}...")
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            add_river_triples(g, row)
            count += 1
            
            if count % 100 == 0:
                print(f"Processed {count} rivers...")
    
    print(f"Serializing {len(g)} triples to {output_ttl}...")
    g.serialize(destination=output_ttl, format='turtle')
    
    print(f"Graph built successfully!")
    print(f"Total triples: {len(g)}")
    print(f"Saved to: {output_ttl}")

if __name__ == "__main__":
    main()
