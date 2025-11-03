# Formulas and Figures Placement Guide

**Document Purpose**: Guide for adding 7 formulas and 4 essential figures to the paper

**Date**: November 3, 2025

---

## FORMULA PLACEMENTS

### Formula 1: Accuracy
**Location**: Section "Evaluation Metrics" (after line 97)

**Formula**:
\[
\text{Accuracy} = \frac{\text{Correct Answers}}{\text{Total Questions}} \times 100\%
\]

---

### Formula 2: Abstention Precision (AP)
**Location**: Section "Evaluation Metrics" (after line 98)

**Formula**:
\[
\text{AP} = \frac{\text{Appropriate Abstentions}}{\text{Total Abstentions}} = \frac{|\{q \in Q : \text{abstain}(q) \land \neg\text{entailed}(q, \mathcal{G})\}|}{|\{q \in Q : \text{abstain}(q)\}|}
\]

Where: \( Q \) = questions, \( \mathcal{G} \) = knowledge graph

---

### Formula 3: Constraint Violation Rejection Rate (CVRR)
**Location**: Section "Evaluation Metrics" (after line 99)

**Formula**:
\[
\text{CVRR} = \frac{|\{(s,p,o) : \text{violates}((s,p,o), \Phi) \land \text{rejected}((s,p,o))\}|}{|\{(s,p,o) : \text{violates}((s,p,o), \Phi)\}|}
\]

Where: \( (s,p,o) \) = triple, \( \Phi \) = SHACL constraints

---

### Formula 4: False Answer Rate (FAR-NE)
**Location**: Section "Evaluation Metrics" (after line 100)

**Formula**:
\[
\text{FAR-NE} = \frac{|\{q \in Q_{\text{NE}} : \text{answered}(q) \land \neg\text{correct}(q)\}|}{|Q_{\text{NE}}|}
\]

Where: \( Q_{\text{NE}} \) = non-entailed questions

---

### Formula 5: Licensed Answer Accuracy (LA)
**Location**: Section "Evaluation Metrics" (after line 101)

**Formula**:
\[
\text{LA} = \frac{|\{q \in Q_{\text{E}} : \text{licensed}(q) \land \text{correct}(q)\}|}{|\{q \in Q_{\text{E}} : \text{licensed}(q)\}|}
\]

Where: \( Q_{\text{E}} \) = entailed questions

---

### Formula 6: Validation Function
**Location**: Section "Model Integration" (after line 52)

**Formula**:
\[
\text{validate}(t, \mathcal{G}, \Phi) = \begin{cases}
\text{license} & \text{if } t \in \mathcal{G} \land \text{satisfies}(t, \Phi) \\
\text{abstain} & \text{otherwise}
\end{cases}
\]

Where: \( t \) = triple, \( \mathcal{G} \) = graph, \( \Phi \) = constraints

---

### Formula 7: Statistical vs. Architectural
**Location**: Section "Discussion" (after line 230)

**Formula**:
\[
\lim_{|\mathcal{D}| \to \infty} P(\text{hallucination} \mid \text{statistical}) > 0 \quad \text{while} \quad P(\text{hallucination} \mid \text{oracle}) = 0
\]

Where: \( \mathcal{D} \) = training data

---

## FIGURE PLACEMENTS

### Figure 1: RAG Comparison
**Location**: After line 172 (Graph-Based RAG section)

**Caption**:
> **Figure 1: RAG System Comparison.** Both systems achieve ~89% accuracy (statistically equivalent, Δ=0.4pp). However, only Graph-RAG provides formal validation, deterministic abstention, and full provenance through architectural enforcement rather than statistical optimization. Text below shows key architectural differences.

**Why**: Shows core thesis—architectural differences matter despite equal accuracy.

---

### Figure 2: Experimental Progression  
**Location**: After line 194 (Summary of Findings)

**Caption**:
> **Figure 2: Experimental Progression.** Statistical learning (fine-tuning) degrades performance by 8pp. Introducing retrieval context via RAG yields +39pp improvement. Graph-RAG maintains high accuracy while adding architectural guarantees. Demonstrates that factual reliability arises from architectural enforcement, not parameter accumulation.

**Why**: Complete experimental narrative in one view.

---

### Figure 3: Capabilities Matrix
**Location**: After line 187 (Licensing Oracle Performance)

**Caption**:
> **Figure 3: Architectural Capabilities Matrix.** Only Graph-RAG (highlighted row) provides the complete capability set across all six dimensions. Simple text indicates capability level (YES/NO/PARTIAL). Accuracy shown on right demonstrates that Graph-RAG uniquely combines high performance with formal guarantees.

**Why**: Qualitative comparison not shown in tables.

---

### Figure 4: Epistemic Discipline
**Location**: After line 143 (Fine-Tuning Results) or with Figure 2

**Caption**:
> **Figure 4: Epistemic Discipline Comparison.** Abstention Precision (green bars) measures how well systems know when to say "I don't know"—fine-tuning achieves only 56.7% (near random chance at 50%), RAG has no abstention mechanism, while Graph-RAG achieves perfect 100%. False Answer Rate (red bars) shows hallucination frequency—only Graph-RAG achieves zero. These metrics demonstrate the epistemic advantage of architectural enforcement.

**Why**: Shows KEY differentiating metrics (epistemic discipline) not redundant with tables.

---

## IMPROVEMENTS APPLIED

### Text Readability
✅ **NO text on colored bars** - all labels moved outside  
✅ **Black text on white** - high contrast everywhere  
✅ **Larger fonts** - easier to read  
✅ **Sans-serif font** - clearer than serif  

### Figure 3 Fix
✅ **Simple text (YES/NO/PARTIAL)** instead of emoji symbols  
✅ **No rendering issues** - works on all systems  

### Figure 4 Replacement
✅ **Meaningful metrics** - Abstention Precision & False Answer Rate  
✅ **Not redundant** - shows epistemic discipline metrics  
✅ **Clear interpretation** - labels explain what's good/bad  

---

## USAGE

```bash
cd /Users/sim/Projects/world_mind/experiments/poc_4_rivers_extended/paper/latest
source /Users/sim/Projects/world_mind/venv/bin/activate
python3 generate_figures.py
```

Files created:
- `figure_1_rag_comparison.png/pdf`
- `figure_2_progression.png/pdf`
- `figure_3_capabilities.png/pdf`
- `figure_4_epistemic_discipline.png/pdf`

---

## COLOR SCHEME

- Red (#D32F2F) - Poor performance
- Orange (#F57C00) - Marginal improvement  
- Blue (#1976D2) - Good performance
- Green (#388E3C) - Best/architectural solution
- Teal (#00838F) - Accent

All colors work in grayscale and are colorblind-friendly.

---

## SUMMARY

**7 Formulas**: Mathematical definitions for all metrics  
**4 Figures**: Essential visualizations not redundant with tables

1. **Figure 1**: RAG architectural comparison
2. **Figure 2**: Complete experimental progression  
3. **Figure 3**: Capabilities matrix (qualitative)
4. **Figure 4**: Epistemic discipline metrics (NEW - replaces redundant cross-domain)

**Integration time**: 30-40 minutes
