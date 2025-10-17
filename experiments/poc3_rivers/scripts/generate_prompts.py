"""
Generate a prompt suite based on actual data in the knowledge graph.
This ensures test cases use real battles and commanders from DBpedia.
"""

import json
import os
from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.namespace import RDFS, XSD
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
GRAPH_PATH = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "prompt_suite.json")

WM = Namespace('http://worldmind.ai/rivers#')


def generate_prompt_suite():
    """Generate rivers prompts from actual graph data."""
    
    print("Loading knowledge graph...")
    g = Graph()
    g.parse(GRAPH_PATH, format='turtle')
    
    prompts = []
    
    # Rivers-specific prompts
    rivers = []
    for river in g.subjects(RDF.type, WM.River):
        label = g.value(river, RDFS.label)
        rivers.append((river, str(label) if label else river.split('/')[-1]))

    print(f"Found {len(rivers)} rivers")

    # Category 1: Valid tributary relation (URIs only)
    print("\nGenerating valid tributary test cases...")
    vt_count = 0
    for river, river_label in rivers:
        for trib in g.objects(river, WM.hasTributary):
            if not isinstance(trib, URIRef):
                continue
            trib_label = g.value(trib, RDFS.label) or URIRef(trib)
            prompts.append({
                "id": f"TR{vt_count+1}",
                "answer": f"{str(trib_label)} is a tributary of {river_label}.",
                "claim": {
                    "subject": str(river),
                    "predicate": "http://worldmind.ai/rivers#hasTributary",
                    "object": str(trib)
                },
                "expected": "ANSWER",
                "category": "tributary_valid"
            })
            vt_count += 1
            if vt_count >= 5:
                break
        if vt_count >= 5:
            break

    # Category 2: Made-up tributary (mismatch pair of two URI rivers)
    print("Generating made-up tributary test cases...")
    only_uri_rivers = [rv for rv in [r[0] for r in rivers] if isinstance(rv, URIRef)]
    if len(only_uri_rivers) >= 2:
        r1, r2 = only_uri_rivers[0], only_uri_rivers[-1]
        prompts.append({
            "id": f"TRX1",
            "answer": f"{g.value(r2, RDFS.label)} is a tributary of {g.value(r1, RDFS.label)}.",
            "claim": {
                "subject": str(r1),
                "predicate": "http://worldmind.ai/rivers#hasTributary",
                "object": str(r2)
            },
            "expected": "ABSTAIN",
            "category": "tributary_invalid_not_in_graph"
        })

    # Category 3: Source and mouth statements (URIs only)
    print("Generating source/mouth test cases...")
    sm_count = 0
    for river, river_label in rivers:
        source = next((x for x in g.objects(river, WM.hasSource) if isinstance(x, URIRef)), None)
        mouth = next((x for x in g.objects(river, WM.hasMouth) if isinstance(x, URIRef)), None)
        if source is not None:
            src_label = g.value(source, RDFS.label) or source
            prompts.append({
                "id": f"SRC{sm_count+1}",
                "answer": f"The source of {river_label} is {str(src_label)}.",
                "claim": {
                    "subject": str(river),
                    "predicate": "http://worldmind.ai/rivers#hasSource",
                    "object": str(source)
                },
                "expected": "ANSWER",
                "category": "source_valid"
            })
            sm_count += 1
        if mouth is not None and sm_count < 6:
            mouth_label = g.value(mouth, RDFS.label) or mouth
            prompts.append({
                "id": f"MTH{sm_count+1}",
                "answer": f"The mouth of {river_label} is {str(mouth_label)}.",
                "claim": {
                    "subject": str(river),
                    "predicate": "http://worldmind.ai/rivers#hasMouth",
                    "object": str(mouth)
                },
                "expected": "ANSWER",
                "category": "mouth_valid"
            })
            sm_count += 1
        if sm_count >= 8:
            break
    
    # Save to file
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(prompts, f, indent=2)
    
    print(f"\n✅ Generated {len(prompts)} prompts")
    print(f"   Saved to: {OUTPUT_PATH}")
    
    # Print summary
    categories = {}
    for p in prompts:
        cat = p['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBreakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Print a few examples
    print("\nSample prompts:")
    for p in prompts[:3]:
        print(f"  [{p['id']}] {p['answer']} → {p['expected']}")


if __name__ == "__main__":
    generate_prompt_suite()

