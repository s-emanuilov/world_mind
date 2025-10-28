# Quick Reference: Experimental Results Summary

## Core Thesis
Hallucination in LLMs is an **architectural limitation**, not a statistical deficiency. Truth-constrained architectures that enforce epistemic boundaries through formal validation outperform parameter optimization approaches.

---

## Experimental Design

### Dataset
- **9,538 river entities** from DBpedia with 21 structured attributes
- **17,726 question-answer pairs** (5-option multiple choice)
- **118,047 RDF triples** in formal knowledge graph
- **SHACL constraints** for validation (elevation, consistency, type checking)

### Five Approaches Evaluated
1. **Baseline LLMs** (no grounding)
2. **Fine-tuning for factual recall** (parameter optimization)
3. **Fine-tuning for abstention** (learned epistemic calibration)
4. **Embedding-based RAG** (statistical retrieval)
5. **Graph-RAG with licensing oracle** (architectural enforcement)

---

## Key Results

| Approach | Accuracy | Key Finding |
|----------|----------|-------------|
| **Gemma 3-4B Baseline** | 16.7% | Compact models severely lack factual knowledge |
| **Claude Sonnet 4.5** | 42.0% | Even frontier models barely exceed chance |
| **Gemini 2.5 Flash Lite** | 50.1% | Best baseline still unreliable |
| **Gemma-Factual (Fine-tuned)** | 8.5% | **Degradation**: Fine-tuning failed to encode facts |
| **Gemma-Abstain (Fine-tuned)** | 8.6% | **Non-deterministic**: Abstention precision 56.7% |
| **RAG (Embedding-based)** | 89.5% | **+39.4pp improvement**: Context provision dominates |
| **Graph-RAG (Oracle)** | 89.1% | **Equivalent accuracy + formal guarantees** |

---

## Critical Insights

### 1. Statistical Learning Fails
- Fine-tuning on 17K examples **degraded** performance (16.7% → 8.5-8.6%)
- Explicit abstention training achieved only 56.7% precision (barely > random)
- **Conclusion**: Parameter optimization cannot encode epistemic boundaries

### 2. Context Provision is Dominant
- Both RAG systems achieved ~89% accuracy (39pp improvement)
- Retrieval quality (not generation architecture) governs factual performance
- **Conclusion**: Access to relevant information is the primary factor

### 3. Architecture Enables Unique Capabilities
Despite equivalent accuracy, only Graph-RAG provides:
- ✓ **Deterministic abstention** via SHACL validation
- ✓ **Formal verification** of factual claims
- ✓ **Interpretable provenance** through triple chains
- ✓ **Domain transfer** without retraining embeddings
- ✓ **Constraint enforcement** (e.g., elevation violations)

---

## The Licensing Oracle Paradigm

**Standard RAG**: Graph as retrieval source (passive)
```
Question → Retrieve context → LLM generates → Output
```

**Graph-RAG Oracle**: Graph as validation gate (active)
```
Question → Retrieve subgraph → LLM proposes → Extract claims → 
Validate vs SHACL → [Pass: Output | Fail: ABSTAIN]
```

**Key distinction**: Claims must be **licensed** by the oracle before generation—a structural constraint that cannot be bypassed probabilistically.

---

## Methodology Highlights

### Data Pipeline
1. **SPARQL extraction** from DBpedia (9,538 rivers)
2. **LLM augmentation** for missing values (Gemini 2.5 Flash Lite)
3. **Question synthesis** with quality controls (self-contained, plausible distractors)
4. **Answer randomization** to eliminate positional bias

### Knowledge Graph Construction
- **RDF modeling** with custom ontology (6 classes, 20+ properties)
- **SHACL constraints** encode domain knowledge (elevation rules, type consistency)
- **Multi-hop retrieval** (2-hop subgraphs provide structured context)

### Claim Verification
- **GLiNER extraction** identifies entities and relationships in LLM responses
- **SHACL validation** checks each claim against formal constraints
- **Binary licensing**: Claim passes all checks → Answer; else → Abstain

---

## Figure Summary

1. **Baseline Performance**: All models struggle (16.7-50.1%)
2. **Fine-Tuning Failure**: Degradation despite supervision
3. **RAG Comparison**: Equivalent accuracy, different architectures
4. **Complete Progression**: Clear narrative from statistical → architectural
5. **Capabilities Matrix**: Only Graph-RAG provides full capability set

---

## Implications

### For LLM Architecture
- **Native integration** of validation gates at token level
- **Abstention as first-class mode** with explicit confidence thresholds
- **Hybrid representations**: Dense vectors for matching + graphs for validation

### For Hallucination Mitigation
- **Not a data problem**: More training data won't fix architectural limitations
- **Not a scale problem**: Frontier models still hallucinate without grounding
- **Architectural solution required**: Structural enforcement, not statistical optimization

### For Production Systems
- **RAG is insufficient** for high-stakes applications requiring formal guarantees
- **Licensing oracles** provide deterministic behavior and auditability
- **Domain portability**: Ontological frameworks transfer without retraining

---

## Public Artifacts

All resources available at HuggingFace: `@s-emanuilov`

**Datasets**:
- `rivers-knowledge-base-v4` (raw + augmented CSVs)
- `rivers-qa-v4` (17,726 Q&A pairs)
- `rivers-knowledge-graph-v4` (118K triples + ontology + SHACL)
- `rivers-evaluation-results-v4` (111K+ evaluation records)

**Models**:
- `gemma-3-4b-rivers-factual` (LoRA fine-tuned)
- `gemma-3-4b-rivers-abstain` (LoRA fine-tuned)

**Code**: `github.com/s-emanuilov/world-mind-poc-rivers` (MIT license)

---

## Citation

```bibtex
@article{emanuilov2025truthconstrained,
  title={Experimental Validation of Truth-Constrained Generation 
         via Graph-Licensed Abstention},
  author={Emanuilov, Simeon and [Co-authors]},
  year={2025},
  note={HuggingFace: s-emanuilov}
}
```

---

## One-Sentence Summary

We demonstrate that architectural enforcement of truth conditions through a graph-based licensing oracle achieves equivalent accuracy to statistical RAG while uniquely enabling deterministic abstention, formal verification, and domain-transferable validation—validating the thesis that hallucination is an architectural limitation requiring structural solutions.

---

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: Ready for publication


