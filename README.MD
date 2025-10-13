# World Mind: Truth-Constrained LLM Architectures

A framework for building LLM systems that use knowledge graphs as "Licensing Oracles" to enforce truth constraints and enable principled abstention.

## Project Philosophy

This project demonstrates a novel architectural approach to reducing LLM hallucination. Rather than treating knowledge graphs as mere retrieval sources (as in standard Graph-RAG), we use them as **non-negotiable validators** that license or deny the generation of factual claims. 

Key insight: The knowledge graph is not a database to query for information—it's a gatekeeper that enforces ontological grounding.

See [INFO.MD](INFO.MD) for the full strategic framework and research contribution.

## Project Structure

```
world_mind/
├── worldmind/              # Core library (reusable components)
│   ├── graph_store.py      # Knowledge graph loading
│   └── models/             # Auditor and policy models
├── experiments/            # Individual experiments/POCs
│   └── poc1_philosophers/  # POC1: Philosophers influence relationships
│       ├── ontology/       # Experiment-specific ontology & constraints
│       ├── data/          # Data and prompts
│       ├── scripts/       # Data fetching, building, evaluation
│       └── configs/       # Configuration
└── requirements.txt       # Python dependencies
```

## Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run POC1 (Philosophers):**
   ```bash
   # Quick run from root
   make poc1
   
   # Or work directly in the experiment directory
   cd experiments/poc1_philosophers
   make all
   ```

## Working with Experiments

Each experiment is self-contained in `experiments/`. To create a new experiment:

1. Copy the structure from `poc1_philosophers/`
2. Define your own ontology in `ontology/`
3. Create your data fetching script in `scripts/get_data.py`
4. Define your prompt suite in `data/prompt_suite.json`
5. Run `make all` in the experiment directory

## Core Library

The `worldmind/` package provides reusable components:

- **GraphStore**: Load and manage RDF knowledge graphs
- **ConsistencyAuditor**: Validate claims against SHACL constraints
- **AbstentionPolicy**: Map validation results to decisions (ANSWER/ABSTAIN)

Import in your experiments:
```python
from worldmind import GraphStore, ConsistencyAuditor, AbstentionPolicy
```

## Available Experiments

### POC1: Philosophers
Tests truth-constrained generation on philosophical influence relationships with temporal constraints.

See [experiments/poc1_philosophers/README.md](experiments/poc1_philosophers/README.md) for details.

### POC2: Military Battles
Tests truth-constrained generation on military battles and commanders with temporal and nationality constraints. Demonstrates multi-hop reasoning across Battle → Commander → Country relationships.

See [experiments/poc2_battles/README.md](experiments/poc2_battles/README.md) for details.

## Research Contribution

**Graph-Licensed Abstention**: A novel LLM architecture where abstention is not a failure mode but a principled response when claims lack evidence or violate formal constraints.

This moves beyond standard Graph-RAG by:
- Making the KG an **integral component** of the generation loop
- Enforcing constraints **deterministically** rather than probabilistically
- Treating abstention as a **correct output** rather than an error

## License

See LICENSE file for details.
