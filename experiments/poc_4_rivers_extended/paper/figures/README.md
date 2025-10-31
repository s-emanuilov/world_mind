# Experimental Figures

This folder contains all publication-quality figures for the Rivers experimental validation paper.

## Generated Figures

### Figure 1: Baseline Performance
**Files**: `figure_1_baseline_performance.png` (144 KB) / `.pdf` (42 KB)

Shows the performance of three baseline LLM models without any grounding mechanisms on the river Q&A dataset. All models struggle with factual recall (16.7-50.1% accuracy), barely exceeding random chance (20% for 5-option multiple choice). Includes reference line for random chance and question counts for each evaluation.

**Key finding**: Even frontier models like Claude Sonnet 4.5 achieve only 42% accuracy, demonstrating that LLMs lack architectural mechanisms for epistemic self-awareness.

---

### Figure 2: Fine-Tuning Results
**Files**: `figure_2_finetuning_results.png` (258 KB) / `.pdf` (48 KB)

Two-panel figure showing:
- **Left panel**: Accuracy comparison showing both fine-tuned variants (factual and abstention) exhibit performance degradation compared to baseline (16.7% → 8.5-8.6%)
- **Right panel**: Abstention behavior breakdown for Gemma-Abstain showing non-deterministic abstention with only 56.7% precision (barely better than random)

**Key finding**: Parameter optimization cannot reliably encode factual knowledge or epistemic discipline, supporting the need for architectural solutions.

---

### Figure 3: RAG Comparison
**Files**: `figure_3_rag_comparison.png` (190 KB) / `.pdf` (54 KB)

Direct comparison of embedding-based RAG and graph-based RAG with licensing oracle. Shows statistically equivalent accuracy (~89%, Δ=0.4pp), but highlights architectural differences:
- Embedding RAG: No validation, no abstention, no provenance
- Graph-RAG: SHACL validation, deterministic abstention, triple provenance

**Key finding**: Retrieval quality dominates factual accuracy, but only architectural enforcement enables formal guarantees.

---

### Figure 4: Complete Progression
**Files**: `figure_4_complete_progression.png` (277 KB) / `.pdf` (50 KB)

Comprehensive bar chart showing the experimental journey across all six approaches:
1. Gemma-3-4B Baseline (16.7%)
2. Gemma-Factual Fine-tuned (8.5%)
3. Gemma-Abstain Fine-tuned (8.6%)
4. Gemini Baseline (50.1%)
5. RAG Embedding (89.5%)
6. Graph-RAG Oracle (89.1%)

Includes visual annotations for "Statistical Learning" vs "Architectural Enforcement" approaches, with arrows showing degradation in fine-tuning and +39.4pp jump with context provision.

**Key finding**: Clear narrative from statistical learning (fails) to architectural enforcement (succeeds).

---

### Figure 5: Capabilities Matrix
**Files**: `figure_5_capabilities_matrix.png` (255 KB) / `.pdf` (60 KB)

Heatmap-style comparison matrix evaluating all five approaches across six capabilities:
- High Factual Accuracy (>80%)
- Deterministic Abstention
- Formal Validation
- Interpretable Provenance
- Domain Transfer
- Zero Retraining

Uses checkmarks (✓), crosses (✗), and half-circles (◐) to indicate full, absent, or partial capability. Only Graph-RAG (highlighted row) provides the complete capability set.

**Key finding**: Graph-RAG uniquely combines high accuracy with formal guarantees—capabilities that emerge from architectural enforcement rather than statistical optimization.

---

## Technical Specifications

- **Resolution**: 300 DPI (publication-ready)
- **Formats**: PNG (for quick viewing), PDF (vector graphics for publication)
- **Color scheme**: Consistent across all figures
  - Red (#E74C3C): Baseline/poor performance
  - Orange (#F39C12): Fine-tuning/marginal improvement
  - Blue (#3498DB): RAG/strong performance
  - Green (#2ECC71): Graph-RAG/architectural innovation
  - Gray (#95A5A6): Abstention/uncertainty
- **Font**: Times New Roman (publication standard)
- **Style**: Academic publication-ready with consistent theming

## Regenerating Figures

To regenerate all figures:

```bash
cd /Users/sim/Projects/world_mind/experiments/poc_4_rivers_extended/paper
source /Users/sim/Projects/world_mind/venv/bin/activate
export MPLCONFIGDIR=/tmp/matplotlib
python generate_figures.py
```

The script automatically saves figures to this directory in both PNG and PDF formats.

## Usage in LaTeX

```latex
\begin{figure}[ht]
\centering
\includegraphics[width=0.8\textwidth]{figures/figure_1_baseline_performance.pdf}
\caption{Baseline LLM performance...}
\label{fig:baseline}
\end{figure}
```

## File Sizes

| Figure | PNG Size | PDF Size | Description |
|--------|----------|----------|-------------|
| Figure 1 | 144 KB | 42 KB | Baseline performance (3 bars) |
| Figure 2 | 258 KB | 48 KB | Fine-tuning results (2 panels) |
| Figure 3 | 190 KB | 54 KB | RAG comparison (2 bars + annotations) |
| Figure 4 | 277 KB | 50 KB | Complete progression (6 bars) |
| Figure 5 | 255 KB | 60 KB | Capabilities matrix (5×6 heatmap) |
| **Total** | **1.12 MB** | **254 KB** | All figures |

All figures are optimized for both digital viewing and print publication.

---

**Generated**: October 28, 2025  
**Script**: `generate_figures.py`  
**Status**: Ready for publication





