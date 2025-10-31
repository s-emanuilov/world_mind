# Scaling Experiment: 500 Cards Per Type

## Purpose

This folder contains a scaled version of the epistemic confusion experiment to validate that the results hold at larger scale (1500 total cards vs 800 baseline).

## Rationale

Scaling from 800 to 1500 cards (1.88× increase) tests whether:
1. **Metrics remain stable** - Do AP, CVRR, FAR-NE, LA hold at scale?
2. **Architectural advantages persist** - Does Graph-RAG's advantage remain consistent?
3. **Statistical significance** - Larger sample provides stronger evidence
4. **Paper credibility** - Demonstrates robustness beyond small pilot tests

## Experiment Design

### Card Distribution
- **Entailed (E)**: 500 cards
- **Contradictory (C)**: 500 cards  
- **Unknown (U)**: 500 cards
- **Total**: 1500 cards

### Baseline Comparison
| Metric | Baseline (800 cards) | Scaled (1500 cards) | Delta |
|--------|---------------------|---------------------|-------|
| E cards | 200 | 500 | +2.5× |
| C cards | 400 | 500 | +1.25× |
| U cards | 200 | 500 | +2.5× |
| **Total** | **800** | **1500** | **+1.88×** |

Note: The baseline had 2× more C cards due to multiple constraint types. The scaled experiment uses equal distribution for cleaner statistical analysis.

## Pipeline

```bash
# Navigate to scaling directory
cd /Users/sim/Projects/world_mind/experiments/poc_4_rivers_extended/epistemic_confusion_experiment/scaling

# Generate scaled cards
make cards

# Run evaluations
make eval-all

# Compute metrics
make metrics

# Generate comparison report
make compare
```

## Expected Results

If our thesis is correct, we should see:
- **Graph-RAG metrics remain stable** (AP ~1.0, CVRR ~0.5, FAR-NE ~0.33)
- **KG Oracle metrics remain perfect** (as deterministic baseline)
- **Statistical confidence increases** with larger sample
- **Architectural advantage persists** across scale

## Directory Structure

```
scaling/
├── README.md                    # This file
├── Makefile                     # Automated pipeline for scaled experiment
├── results/
│   ├── scaled_cards.jsonl      # 1500 generated cards
│   ├── kg_results.jsonl        # KG Oracle evaluation
│   ├── graph_rag_results.jsonl # Graph-RAG evaluation
│   ├── all_results.jsonl       # Merged results
│   ├── metrics.json            # Computed metrics
│   ├── report.html             # HTML report
│   └── comparison.json         # Baseline vs scaled comparison
└── SCALING_ANALYSIS.md         # Results analysis (generated after run)

```

## Integration with Paper

This scaling experiment strengthens the paper by:
1. **Demonstrating robustness** - Results aren't artifacts of small samples
2. **Providing statistical power** - 1500 cards enable confident conclusions
3. **Addressing reviewer concerns** - Shows thoroughness and rigor
4. **Supporting claims** - "Validated across 1500 test cases" is stronger than 800

## References

- **Baseline experiment**: `../results/` (800 cards)
- **LLM comparison**: `../llm_test/results/` (30 cards with Claude Sonnet 4)
- **Methodology**: `../README.md`
- **Paper**: `../../paper/Experimental Validation of Truth-Constrained Generation via Graph-Licensed Abstention.pdf`

---

**Status**: 🚧 In Progress  
**Created**: October 30, 2025  
**Target**: Validate thesis at scale for publication


