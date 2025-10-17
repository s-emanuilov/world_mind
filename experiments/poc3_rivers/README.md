# POC 3: US Rivers Experiment

This experiment demonstrates truth-constrained LLM generation using a knowledge graph of US rivers, their tributaries, source and mouth features, traversed states, and physical attributes (length, discharge, basin).

## Structure

```
poc3_rivers/
├── ontology/           # Rivers ontology and SHACL constraints
├── data/               # Raw data, knowledge graph, and prompt suite
├── scripts/            # Data fetching, graph building, and evaluation
├── configs/            # Configuration parameters
└── artifacts/          # Generated evaluation results
```

## Usage

From this directory, run:

```bash
make data        # Fetch rivers data from DBpedia
make build       # Build the rivers knowledge graph
make validate    # Validate graph against SHACL constraints
make generate-answers  # Generate prompts from the graph
make eval-answers      # Run evaluation through Auditor + Policy
```

## Ontology Highlights

- Classes: `River`, `GeographicFeature`
- Object Properties: `hasSource`, `hasMouth`, `hasTributary`, `traverses`, `inCountry`, `drainageBasin`
- Data Properties: `length`, `discharge`, `elevation`

## Constraints

- Tributaries must be instances of `River`
- US rivers should have at least one coverage link (state traversed, source, or mouth)
- Numeric fields have correct datatypes when present


