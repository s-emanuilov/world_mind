# Quick Start Guide

## 1. Run the Complete Pipeline (10 cards per type - fast test)

```bash
cd /Users/sim/Projects/world_mind
source venv/bin/activate
cd experiments/poc_4_rivers_extended/epistemic_confusion_experiment

# Generate test cards
python cards/make_context_cards.py \
    --kg ../graph_rag/data/knowledge_graph.ttl \
    --pred "http://worldmind.ai/rivers-v4#hasMouth" \
    --pred-label "mouth" \
    --num-per-type 10 \
    --out results/test_cards.jsonl

# Evaluate with KG oracle
python eval/run_epistemic_tests.py \
    --cards results/test_cards.jsonl \
    --system kg \
    --out results/test_kg_results.jsonl

# Compute metrics
python eval/metrics_abstention.py \
    --results results/test_kg_results.jsonl \
    --out results/test_metrics.json \
    --verbose

# Generate HTML report
python reporting/html_report.py \
    --results results/test_kg_results.jsonl \
    --metrics results/test_metrics.json \
    --out results/test_report.html

# Open the report
open results/test_report.html
```

## 2. Run with Makefile (easier)

```bash
cd /Users/sim/Projects/world_mind
source venv/bin/activate
cd experiments/poc_4_rivers_extended/epistemic_confusion_experiment

# Quick test (10 cards per type)
make test

# Full pipeline (200 cards per type)
make all

# View help
make help
```

## 3. Expected Output

After running the pipeline, you'll have:

```
results/
├── context_cards.jsonl      # 40 test cards (E/C/U labeled)
├── test_kg_results.jsonl    # Evaluation results
├── test_metrics.json        # Computed metrics
└── test_report.html         # Visual report (open in browser)
```

## 4. Understanding the Results

### Confusion Matrix Example
```
              E (entailed)  C (contradictory)  U (unknown)
ANSWER          10              10               0
ABSTAIN          0              10              10
```

### Key Metrics
- **AP = 1.000**: Perfect abstention precision (all abstentions were correct)
- **CVRR = 0.500**: Caught 50% of contradictory cases
- **FAR-NE = 0.333**: Answered incorrectly 33% of non-entailed cases
- **LA = 1.000**: Perfect accuracy on entailed facts

## 5. Next Steps

### Test Different Predicates
```bash
# Test with tributary relationships
python cards/make_context_cards.py \
    --kg ../graph_rag/data/knowledge_graph.ttl \
    --pred "http://worldmind.ai/rivers-v4#hasTributary" \
    --pred-label "tributary" \
    --out results/tributary_cards.jsonl
```

### Generate Near-Miss Adversarial Cases
```bash
python adversarial/make_near_miss.py \
    --kg ../graph_rag/data/knowledge_graph.ttl \
    --pred "http://worldmind.ai/rivers-v4#hasMouth" \
    --pred-label "mouth" \
    --num 100 \
    --out results/near_miss_cards.jsonl
```

### Customize System Adapters

Edit `eval/run_epistemic_tests.py` to add your own LLM or RAG system:
- Implement `RawLLMAdapter` with your API
- Implement `RAGAdapter` with your embedding model
- Compare against KG oracle baseline

## 6. Troubleshooting

### Module not found errors
```bash
# Make sure you're in the virtual environment
cd /Users/sim/Projects/world_mind
source venv/bin/activate
```

### No triples found
```bash
# Verify the predicate URI matches the ontology
grep "hasMouth" ../graph_rag/data/knowledge_graph.ttl | head -5
```

### Permission denied
```bash
# Make scripts executable
chmod +x cards/*.py eval/*.py adversarial/*.py reporting/*.py
```

## 7. Full Production Run

```bash
# Generate 200 cards per type (800 total)
make clean
make all

# This will take 2-5 minutes
# Output: results/report.html
```

## Documentation

- **README.md**: Full documentation
- **SUMMARY.md**: Experiment overview and methodology
- **../paper/feedback/**: Original feedback documents


