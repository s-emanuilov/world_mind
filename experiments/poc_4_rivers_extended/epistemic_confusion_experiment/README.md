# Epistemic Confusion Experiment

This experiment implements the **quantitative abstention precision** evaluation framework described in the paper feedback. It tests whether LLMs hallucinate even when facts and negations are provided in context, and demonstrates that graph-licensed validation can prevent this through architectural enforcement.

## Overview

The experiment generates "context cards" that provide explicit facts in the prompt, then asks questions to test whether systems can:
1. **Answer correctly** when facts are entailed (E)
2. **Abstain or say NO** when facts are contradictory (C)
3. **Abstain or say UNKNOWN** when facts are absent (U)

### Key Innovation

Unlike standard accuracy metrics, this experiment measures **epistemic discipline** through:
- **AP (Abstention Precision)**: Of all abstentions, what fraction were correct?
- **CVRR (Constraint Violation Rejection Rate)**: Of contradictory claims, what fraction were rejected?
- **FAR-NE (False Answer Rate on Non-Entailed)**: How often did systems answer when they should abstain?
- **LA (Licensed Answer Accuracy)**: Of entailed claims, what fraction were answered correctly?

## Architecture

```
Knowledge Graph (TTL)
    ↓
Context Card Generator → Cards (E/C/U labeled)
    ↓
Unified Evaluator → Multiple Systems
    ├── KG Oracle (deterministic)
    ├── Raw LLM (API stub)
    ├── RAG (embedding-based)
    └── Graph-RAG (licensing oracle)
    ↓
Results (JSONL)
    ↓
Metrics Calculator → Abstention Metrics
    ↓
HTML Report → Visual Analysis
```

## Directory Structure

```
epistemic_confusion_experiment/
├── cards/
│   └── make_context_cards.py       # Generate E/C/U labeled test cards
├── eval/
│   ├── run_epistemic_tests.py      # Unified evaluator with pluggable adapters
│   └── metrics_abstention.py       # Compute AP, CVRR, FAR-NE, LA
├── adversarial/
│   └── make_near_miss.py           # Generate near-miss negatives
├── reporting/
│   └── html_report.py              # Generate visual HTML reports
├── results/                        # Output directory for results
├── Makefile                        # Automated pipeline
└── README.md                       # This file
```

## Setup

### Prerequisites

```bash
# Ensure you're in the project virtual environment
cd /Users/sim/Projects/world_mind
source venv/bin/activate

# Install required dependencies (already in requirements.txt)
pip install rdflib pyshacl
```

### Quick Start

```bash
# Navigate to experiment directory
cd experiments/poc_4_rivers_extended/epistemic_confusion_experiment

# Generate context cards
make cards

# Evaluate with KG oracle (deterministic baseline)
make eval-kg

# Compute metrics
make metrics

# Generate HTML report
make report

# Or run entire pipeline
make all
```

## Pipeline Components

### 1. Context Card Generation

Generates test cases with explicit epistemic labels:

```bash
python cards/make_context_cards.py \
    --kg ../graph_rag/data/knowledge_graph.ttl \
    --pred "http://worldmind.ai/rivers-v4#hasMouth" \
    --pred-label "mouth" \
    --num-per-type 200 \
    --out results/context_cards.jsonl
```

**Output format (JSONL):**
```json
{
  "id": "CARD_E_000001",
  "facts": ["Escanaba River mouth Lake Michigan"],
  "question": "Is Lake Michigan the mouth of Escanaba River?",
  "gold": "YES",
  "label": "E",
  "claim": {"subj": "...", "pred": "...", "obj": "..."}
}
```

**Label meanings:**
- **E (Entailed)**: Triple exists in KG → gold=YES
- **C (Contradictory)**: Violates constraints or explicitly negated → gold=NO
- **U (Unknown)**: Not present, not contradictory (open-world) → gold=UNKNOWN

### 2. System Evaluation

Evaluate different systems using the unified evaluator:

```bash
# KG Oracle (deterministic, simulates perfect licensing)
python eval/run_epistemic_tests.py \
    --cards results/context_cards.jsonl \
    --system kg \
    --out results/kg_results.jsonl

# Graph-RAG (with actual KG lookup)
python eval/run_epistemic_tests.py \
    --cards results/context_cards.jsonl \
    --system graph_rag \
    --kg-path ../graph_rag/data/knowledge_graph.ttl \
    --out results/graph_rag_results.jsonl

# Raw LLM (stub - customize RawLLMAdapter in code)
python eval/run_epistemic_tests.py \
    --cards results/context_cards.jsonl \
    --system raw \
    --model gpt-4 \
    --out results/raw_llm_results.jsonl

# RAG (stub - customize RAGAdapter in code)
python eval/run_epistemic_tests.py \
    --cards results/context_cards.jsonl \
    --system rag \
    --out results/rag_results.jsonl
```

**Output format (JSONL):**
```json
{
  "id": "CARD_E_000001",
  "gold": "YES",
  "pred": "YES",
  "pass": true,
  "system": "kg",
  "label": "E"
}
```

### 3. Metrics Computation

Compute abstention precision metrics:

```bash
python eval/metrics_abstention.py \
    --results results/all_results.jsonl \
    --out results/metrics.json \
    --verbose
```

**Key metrics computed:**

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **AP** | (S_C + S_U) / (S_E + S_C + S_U) | Abstention precision |
| **CVRR** | S_C / (S_C + A_C) | Constraint violation rejection rate |
| **FAR-NE** | (A_C + A_U) / (non-entailed) | False answer rate (lower is better) |
| **LA** | A_E / (A_E + S_E) | Licensed answer accuracy |

**Confusion Matrix:**
```
              E (entailed)  C (contradictory)  U (unknown)
ANSWER          A_E              A_C              A_U
ABSTAIN         S_E              S_C              S_U
```

### 4. HTML Report Generation

Generate visual report:

```bash
python reporting/html_report.py \
    --results results/all_results.jsonl \
    --metrics results/metrics.json \
    --out results/report.html
```

Open `results/report.html` in browser to view:
- Summary metrics table
- Confusion matrices per system
- Detailed per-card results
- Color-coded performance indicators

### 5. Adversarial Near-Miss Cases

Generate semantically plausible but factually false test cases:

```bash
python adversarial/make_near_miss.py \
    --kg ../graph_rag/data/knowledge_graph.ttl \
    --pred "http://worldmind.ai/rivers-v4#hasMouth" \
    --pred-label "mouth" \
    --num 500 \
    --out results/near_miss_cards.jsonl
```

These cards test whether systems can distinguish between:
- Coherent-sounding claims
- Actually entailed facts

## Customizing Adapters

The evaluation framework uses pluggable adapters. To add your own LLM or RAG system:

### Adding a Raw LLM Adapter

Edit `eval/run_epistemic_tests.py`, find the `RawLLMAdapter` class:

```python
class RawLLMAdapter(BaseAdapter):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        # Initialize your LLM client here
    
    def answer(self, card: Dict) -> str:
        # Format prompt with card["facts"] and card["question"]
        prompt = self._format_prompt(card)
        
        # Call your LLM API
        response = your_llm_client.generate(prompt)
        
        # Parse response to extract YES/NO/UNKNOWN
        return self._parse_response(response)
```

### Adding a RAG Adapter

Edit `eval/run_epistemic_tests.py`, find the `RAGAdapter` class:

```python
class RAGAdapter(BaseAdapter):
    def __init__(self, embedding_model: str, llm_model: str):
        # Initialize embedding model and vector store
        # Initialize LLM client
        pass
    
    def answer(self, card: Dict) -> str:
        # 1. Embed the question
        query_embedding = self.embed(card["question"])
        
        # 2. Retrieve relevant passages
        passages = self.retrieve(query_embedding, top_k=5)
        
        # 3. Augment prompt with passages
        prompt = self._format_prompt_with_passages(card, passages)
        
        # 4. Query LLM
        response = self.llm_client.generate(prompt)
        
        # 5. Parse and return
        return self._parse_response(response)
```

## Expected Results

### Ideal Graph-Licensed System
- **AP**: > 0.90 (high abstention precision)
- **CVRR**: > 0.90 (catches constraint violations)
- **FAR-NE**: < 0.10 (rarely answers when should abstain)
- **LA**: > 0.90 (answers correctly on entailed facts)

### Typical RAG System
- **AP**: 0.50-0.70 (inconsistent abstention)
- **CVRR**: 0.30-0.50 (weak constraint enforcement)
- **FAR-NE**: 0.50-0.80 (often answers when should abstain)
- **LA**: 0.80-0.90 (good on entailed facts)

### Raw LLM
- **AP**: 0.40-0.60 (poor abstention)
- **CVRR**: 0.20-0.40 (weak constraint detection)
- **FAR-NE**: 0.70-0.90 (almost always answers)
- **LA**: 0.50-0.70 (moderate accuracy)

## Extending the Experiment

### Test Different Predicates

```bash
# Test with hasTributary instead of hasMouth
python cards/make_context_cards.py \
    --kg ../graph_rag/data/knowledge_graph.ttl \
    --pred "http://worldmind.ai/rivers-v4#hasTributary" \
    --pred-label "tributary" \
    --out results/tributary_cards.jsonl
```

### Test Different Domains

To replicate in a new domain (e.g., cities → mayors):
1. Build a knowledge graph for the new domain
2. Define SHACL constraints
3. Use the same card generation and evaluation pipeline
4. Compare metrics across domains

## Troubleshooting

### "No triples found for predicate"
- Check that the predicate URI exactly matches the ontology
- Use `grep "hasMouth" ../graph_rag/data/knowledge_graph.ttl` to verify

### "RDFLIB_AVAILABLE is False"
```bash
pip install rdflib
```

### Adapter returns all UNKNOWN
- This is expected for stub adapters (RawLLMAdapter, RAGAdapter)
- Customize the adapter code to call your actual API

## References

- **Feedback Document**: `../paper/feedback/How_to_Quantify_Abstention_Precision.docx.md`
- **Code Reference**: `../paper/feedback/How_to_Quantify_Abstention_Precision_-_Code.docx.md`
- **Paper**: `../paper/feedback/Experimental Validation of Truth-Constrained Generation via Graph-Licensed Abstention.pdf`

## Citation

If you use this experiment framework, please cite:

```bibtex
@misc{worldmind_epistemic_confusion,
  title={Epistemic Confusion Experiment: Quantifying Abstention Precision in Graph-Licensed Generation},
  author={WorldMind Research},
  year={2025},
  url={https://github.com/s-emanuilov/world-mind}
}
```

## License

MIT License - See project root for details.


