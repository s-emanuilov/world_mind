# POC 1: Philosophers Experiment

This experiment demonstrates truth-constrained LLM generation using a knowledge graph of philosophers and their influence relationships.

## Overview

This POC validates claims about philosophical influence relationships (e.g., "Aristotle studied under Plato") against:
1. **Direct evidence** in the knowledge graph
2. **Temporal constraints** ensuring the student and teacher lifespans overlapped

## Data Source

The knowledge graph is built from DBpedia SPARQL queries that extract:
- Philosophers and scientists
- Their birth and death dates
- Their influence relationships (`dbo:influencedBy`)

## Structure

```
poc1_philosophers/
├── ontology/           # Experiment-specific ontology and constraints
├── data/              # Raw data, knowledge graph, and prompt suite
├── scripts/           # Data fetching, graph building, and evaluation
├── configs/           # Configuration parameters
└── artifacts/         # Generated evaluation results
```

## Usage

From this directory, run:

```bash
# Fetch data from DBpedia
make data

# Build the knowledge graph
make build

# Validate against SHACL constraints
make validate

# Run evaluation
make test

# Clean generated files
make clean

# Run all steps
make all
```

## Key Files

- **ontology/worldmind_core.ttl**: Core classes and properties (Agent, TimeSpan, influencedBy)
- **ontology/worldmind_constraints.shacl.ttl**: SHACL shapes enforcing temporal overlap constraints
- **data/prompt_suite.json**: Canonical test prompts with expected outcomes
- **scripts/get_data.py**: Fetches raw philosopher data from DBpedia
- **scripts/build_graph.py**: Constructs RDF knowledge graph from raw data
- **scripts/validate_graph.py**: Validates graph against SHACL constraints
- **scripts/eval_prompts.py**: Evaluates the abstention policy against test prompts

## Ontology

The experiment uses a minimal ontology with:

**Classes:**
- `wm:Agent` - A person (philosopher or scientist)
- `wm:TimeSpan` - A temporal extent with start and end dates

**Properties:**
- `wm:influencedBy` - Relates a person to their intellectual influence
- `wm:hasTemporalExtent` - Links an agent to their lifespan
- `wm:start`, `wm:end` - Mark temporal boundaries

**Constraints:**
- Agents in an `influencedBy` relationship must have temporally overlapping lifespans

