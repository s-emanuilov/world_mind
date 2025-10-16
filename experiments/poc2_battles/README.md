# POC 2: Military Battles Experiment

This experiment demonstrates truth-constrained LLM generation using a knowledge graph of military battles, commanders, and their temporal/national relationships.

## Overview

This POC validates claims about military commanders and battles against:
1. **Temporal constraints**: Commanders must be alive during the battles they commanded
2. **Nationality alignment**: Commanders' nationalities must match combatant countries in the battle
3. **Multi-hop reasoning**: Battle → Commander → Country relationships

## Data Source

The knowledge graph is built from DBpedia SPARQL queries that extract:
- Military conflicts from 1700 onwards (for better data quality)
- Battle dates and commanders
- Commander birth/death dates and nationalities
- Combatant countries

## Structure

```
poc2_battles/
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

# Generate test prompts from actual graph data
make prompts

# Run evaluation (rule name changed to be explicit)
make eval-answers

# Clean generated files
make clean

# Run all steps (includes prompt generation)
make all
```

## Key Files

- **ontology/worldmind_core.ttl**: Core classes (Battle, Agent, Country, TimeSpan) and properties
- **ontology/worldmind_constraints.shacl.ttl**: SHACL shapes enforcing temporal and nationality constraints
- **data/prompt_suite.json**: Canonical test prompts with expected outcomes
- **scripts/get_data.py**: Fetches battle data from DBpedia (limit 20K)
- **scripts/build_graph.py**: Constructs RDF knowledge graph from raw data
- **scripts/validate_graph.py**: Validates graph against SHACL constraints
- **scripts/eval_prompts.py**: Evaluates the abstention policy against test prompts
 - **scripts/generate_llm_answers.py**: Calls OpenRouter to answer prompts with a chosen LLM
 - **scripts/extract_claims.py**: Uses a fast LLM to extract verifiable claims from answers
 - **scripts/verify_claims.py**: Verifies extracted claims against the knowledge graph

## Ontology

The experiment uses a minimal ontology with:

**Classes:**
- `Battle` - A military conflict
- `Agent` - A military commander
- `Country` - A nation or political entity
- `TimeSpan` - A temporal extent with start and end dates

**Properties:**
- `hasCommander` - Relates a battle to its commander(s)
- `hasCombatant` - Relates a battle to combatant countries
- `hasNationality` - Relates a commander to their country
- `hasTemporalExtent` - Links an agent to their lifespan
- `occurredOn` - The date a battle occurred
- `start`, `end` - Mark temporal boundaries

**Constraints:**
1. Commander must be alive during the battle (temporal overlap)
2. Commander's nationality must match a combatant country in the battle

## Example Violations Detected

- "Julius Caesar commanded at Waterloo" (temporal anachronism - died ~1800 years before)
- "Napoleon commanded at Waterloo in 1820" (wrong date - battle was 1815, Napoleon died 1821)
- "American commander led British forces at Waterloo" (nationality mismatch)
- "Winston Churchill commanded D-Day forces" (wrong role - he was PM, not military commander)

## Multi-Hop Reasoning

The system can validate complex claims like:
- Battle → Commander (1 hop)
- Battle → Commander → Nationality (2 hops)
- Battle → Commander → Lifespan → Overlap with Battle Date (2-3 hops)
- Battle → Combatant Countries → Match Commander Nationality (2 hops)

This demonstrates how World Mind's licensing oracle enforces ontological grounding through deterministic constraint checking, not probabilistic retrieval.

