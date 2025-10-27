# Graph-RAG Experiment for Rivers Extended Dataset

This experiment implements a **Graph-based RAG** system with **verification oracle** as described in INFO.MD.

## Overview

Demonstrates superiority of Graph-RAG over pure embedding-based RAG by:
1. Building knowledge graph from river data
2. Retrieving relevant subgraphs instead of text chunks
3. Using GLiNER for claim extraction
4. Verifying claims against SHACL constraints (licensing oracle)
5. Applying abstention policy for unsupported claims

## Architecture

```
Question → Graph Retrieval → Subgraph → LLM → Extract Claims → Verify → Abstain or Answer
```

## Key Components

### 1. Knowledge Graph (`data/knowledge_graph.ttl`)
- Built from `raw_rivers_filled.csv`
- Contains rivers, geographic features, relationships
- Structured as RDF triples

### 2. Graph Retrieval (`scripts/graph_retrieval.py`)
- Retrieves subgraphs instead of text chunks
- Multi-hop traversal (default: 2 hops)
- Returns structured context

### 3. Claim Extraction (`scripts/extract_claims.py`)
- Uses GLiNER for named entity recognition
- Extracts factual triples from LLM responses
- Prepares claims for verification

### 4. Verification Oracle (`scripts/verify_claims.py`)
- Validates claims against SHACL constraints
- Implements licensing check
- Enforces ontological constraints

### 5. Evaluation (`scripts/evaluate_graph_rag.py`)
- Complete Graph-RAG pipeline
- Compares against baseline RAG
- Tracks accuracy metrics

## Setup

```bash
# Install dependencies
pip install -r ../../../requirements.txt

# Build knowledge graph from CSV
cd scripts
python build_graph.py

# Verify graph
python validate_graph.py
```

## Running Experiments

```bash
# Run Graph-RAG evaluation
python scripts/evaluate_graph_rag.py --model google/gemini-2.5-flash-lite --max-questions 100

# Compare with baseline RAG
python scripts/compare_with_rag.py
```

## Expected Results

1. **Graph-RAG Accuracy**: Should exceed 90% (vs baseline RAG at 89%)
2. **Claim Verification**: Shows licensing oracle preventing hallucinations
3. **Abstention Rate**: Measures principled withholding when evidence is absent

## Verification Metrics

- **Licensing Accuracy**: % of claims that pass SHACL validation
- **Constraint Violations**: Detected violations of ontological rules
- **Abstention Rate**: % of responses where system correctly abstains

## Key Innovation

Unlike standard Graph-RAG which uses graphs as retrieval source, this system:
1. **Retrieves structured subgraphs** (not just text)
2. **Extracts claims** from LLM responses
3. **Verifies claims against graph** using SHACL
4. **Enforces abstention** when claims are unlicensed

This implements the **"Truth-Constrained Generation via Graph-Licensed Abstention"** approach from INFO.MD.
