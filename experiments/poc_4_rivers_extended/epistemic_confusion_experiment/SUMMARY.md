# Epistemic Confusion Experiment - Summary

## Purpose

This experiment implements the **quantitative abstention precision** evaluation framework to measure how well different systems can distinguish between:
- **Entailed facts** (should answer YES)
- **Contradictory facts** (should answer NO or abstain)
- **Unknown facts** (should abstain or say UNKNOWN)

## Key Innovation

Unlike traditional accuracy metrics, this framework measures **epistemic discipline** - the ability to know what you don't know. It quantifies the licensing advantage of Graph-RAG systems over statistical approaches (raw LLMs, fine-tuning, embedding-based RAG).

## Methodology

### Context Cards

Generates test cases with three epistemic labels:
- **E (Entailed)**: Facts in the knowledge graph
- **C (Contradictory)**: Facts that violate SHACL constraints or are explicitly negated
- **U (Unknown)**: Facts not present and not provably wrong

Each card provides explicit facts in context and asks a yes/no question.

### Confusion Matrix

Maps system actions (Answer/Abstain) against ground truth (E/C/U):

```
              E (entailed)  C (contradictory)  U (unknown)
ANSWER          A_E              A_C              A_U
ABSTAIN         S_E              S_C              S_U
```

### Metrics

1. **AP (Abstention Precision)**: `(S_C + S_U) / (S_E + S_C + S_U)`
   - Of all abstentions, what fraction were correct?
   - High AP = principled abstention

2. **CVRR (Constraint Violation Rejection Rate)**: `S_C / (S_C + A_C)`
   - Of contradictory cases, what fraction were rejected?
   - High CVRR = strong constraint enforcement

3. **FAR-NE (False Answer Rate on Non-Entailed)**: `(A_C + A_U) / (non-entailed)`
   - How often did system answer when it should abstain?
   - Low FAR-NE = good epistemic discipline (lower is better)

4. **LA (Licensed Answer Accuracy)**: `A_E / (A_E + S_E)`
   - Of entailed cases, what fraction were answered correctly?
   - High LA = doesn't suppress valid answers

## Expected Results

### Graph-Licensed System (Target)
- **AP**: > 0.90 (high precision)
- **CVRR**: > 0.90 (catches violations)
- **FAR-NE**: < 0.10 (rarely wrong)
- **LA**: > 0.90 (answers correctly)

### Standard RAG
- **AP**: 0.50-0.70 (inconsistent)
- **CVRR**: 0.30-0.50 (weak enforcement)
- **FAR-NE**: 0.50-0.80 (often wrong)
- **LA**: 0.80-0.90 (good when it answers)

### Raw LLM
- **AP**: 0.40-0.60 (poor)
- **CVRR**: 0.20-0.40 (very weak)
- **FAR-NE**: 0.70-0.90 (almost always answers)
- **LA**: 0.50-0.70 (moderate)

## Pipeline

```bash
# Generate test cards
make cards

# Evaluate systems
make eval-all

# Compute metrics
make metrics

# Generate report
make report

# Or run everything
make all
```

## Output

1. **context_cards.jsonl**: Test cases with E/C/U labels
2. **kg_results.jsonl**: KG oracle evaluation results
3. **graph_rag_results.jsonl**: Graph-RAG evaluation results
4. **metrics.json**: Computed abstention metrics
5. **report.html**: Visual HTML report with tables and statistics

## Integration with Paper

This experiment directly addresses the feedback in:
- `../paper/feedback/How_to_Quantify_Abstention_Precision.docx.md`
- `../paper/feedback/How_to_Quantify_Abstention_Precision_-_Code.docx.md`

It provides the quantitative evidence to demonstrate that:
1. Statistical learning (fine-tuning) cannot reliably encode epistemic boundaries
2. Embedding-based RAG lacks structural mechanisms for principled abstention
3. Graph-licensed systems achieve superior abstention precision through architectural enforcement

## Key Files

- **cards/make_context_cards.py**: Generates E/C/U labeled test cases from KG
- **eval/run_epistemic_tests.py**: Unified evaluator with pluggable adapters
- **eval/metrics_abstention.py**: Computes AP, CVRR, FAR-NE, LA metrics
- **reporting/html_report.py**: Generates visual HTML reports
- **adversarial/make_near_miss.py**: Creates challenging near-miss cases
- **Makefile**: Automates the entire pipeline
- **README.md**: Detailed usage instructions

## Dependencies

- Python 3.10+
- rdflib (for RDF graph operations)
- pyshacl (optional, for SHACL validation)

All dependencies are in the project's main requirements.txt.

## Customization

To adapt this experiment for a different domain:
1. Point to your knowledge graph TTL file
2. Specify your predicate URI
3. Run the same pipeline
4. Compare metrics across domains

The framework is domain-agnostic and reusable.

## Citation

This experiment implements the evaluation methodology proposed in:

*"Experimental Validation of Truth-Constrained Generation via Graph-Licensed Abstention"*

See `../paper/feedback/` for full technical specifications.


