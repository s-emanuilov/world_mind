# Rivers Knowledge Graph with Formal Ontology and Constraints

This repository contains a complete RDF knowledge graph with 118,047 triples representing structured knowledge about U.S. rivers, accompanied by a formal domain ontology and SHACL constraint definitions for validation. The knowledge graph is built from the rivers knowledge base and structured using a custom ontology (`worldmind_core.ttl`) defining six core classes (River, GeographicFeature, State, County, Country, RiverSystem) and 20+ properties for hydrological metrics, geographic relationships, and administrative hierarchies. SHACL shapes (`worldmind_constraints.shacl.ttl`) encode domain knowledge as machine-executable validation rules, including elevation constraints (source must exceed mouth), positive value requirements for measurements, geographic consistency checks, and tributary type validation. This knowledge graph implements the "licensing oracle" architecture where the graph functions as a mandatory validation gate for factual claims rather than merely a retrieval source. The formal ontology and constraints enable deterministic abstention, claim verification against logical rules, and domain-transferable validation mechanisms for truth-constrained LLM generation.

## Files

- `knowledge_graph.ttl` (RDF format) - 118,047 triples representing river knowledge
- `worldmind_core.ttl` - Domain ontology with 6 classes and 20+ properties
- `worldmind_constraints.shacl.ttl` - SHACL shapes for formal validation

## Ontology Classes

- **River**: Primary entity with data properties for length, discharge, watershed
- **GeographicFeature**: Source mountains, mouth water bodies, named locations
- **State**: U.S. state administrative divisions
- **County**: County-level subdivisions
- **Country**: National entities for international rivers
- **RiverSystem**: Major watershed systems (e.g., Mississippi River System)

## SHACL Constraints

1. **Elevation constraints**: Source elevation > mouth elevation (gravity-fed flow)
2. **Positive value constraints**: Length, discharge, elevation ≥ 0
3. **Geographic consistency**: Rivers flow through jurisdictions consistent with source/mouth
4. **Tributary type constraints**: Proper domain and range types for relationships

## Usage

```python
from rdflib import Graph

# Load knowledge graph
g = Graph()
g.parse('knowledge_graph.ttl', format='turtle')

# Query example: Find rivers in California
query = """
PREFIX : <http://worldmind.ai/rivers#>
PREFIX dbr: <http://dbpedia.org/resource/>

SELECT ?river ?length WHERE {
    ?river a :River ;
           :flowsThrough dbr:California ;
           :length ?length .
}
ORDER BY DESC(?length)
LIMIT 10
"""

results = g.query(query)
for row in results:
    print(f"River: {row.river}, Length: {row.length}m")

# Validate against SHACL constraints
from pyshacl import validate

shapes_g = Graph()
shapes_g.parse('worldmind_constraints.shacl.ttl', format='turtle')

conforms, results_graph, results_text = validate(
    g, shacl_graph=shapes_g, inference='rdfs'
)

print(f"Validation: {'PASS' if conforms else 'FAIL'}")
if not conforms:
    print(results_text)
```

## Licensing Oracle Architecture

Unlike standard knowledge graphs used for retrieval, this graph implements a licensing oracle that:
1. **Validates claims** against SHACL constraints before generation
2. **Enforces abstention** when claims are unlicensed or violate constraints
3. **Provides provenance** through explicit triple chains
4. **Enables domain transfer** without retraining embeddings

## Statistics

- **Total triples**: 118,047
- **River entities**: 9,538
- **Geographic features**: 3,200+
- **States**: 50
- **Counties**: 800+
- **Constraint rules**: 15 SHACL shapes

## Citation

```bibtex
@dataset{emanuilov2025rivers_kg,
  author = {Emanuilov, Simeon},
  title = {Rivers Knowledge Graph with Formal Ontology and SHACL Constraints},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/datasets/s-emanuilov/rivers-knowledge-graph}}
}
```

## License

- Knowledge graph content: CC BY-SA 3.0 (derived from DBpedia)
- Ontology and SHACL shapes: MIT License


