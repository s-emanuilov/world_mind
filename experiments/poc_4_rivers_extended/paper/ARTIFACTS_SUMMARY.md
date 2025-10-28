# Public Artifacts for World Mind POC-4 Rivers Extended

This document lists all artifacts developed during the experimental validation of truth-constrained generation via graph-licensed abstention, prepared for public release.

## HuggingFace Username
`s-emanuilov`

---

## 1. Datasets

### 1.1 River Knowledge Base

**Repository**: `https://huggingface.co/datasets/s-emanuilov/rivers-knowledge-base-v4`

**Contents**:
- `raw_rivers.csv` (5.3MB) - 9,538 river entities with 21 attributes from DBpedia
- `raw_rivers_filled.csv` (6.2MB) - Enhanced with LLM-augmented missing values

**Attributes**: length, discharge, watershed, source/mouth locations and elevations, tributary relationships, state/county classifications, river systems

**Description**: Structured knowledge base extracted from DBpedia SPARQL endpoint, representing U.S. river entities with hydrological metrics, geographic relationships, and administrative metadata. Serves as ground truth for question generation and knowledge graph construction.

---

### 1.2 Question-Answer Dataset

**Repository**: `https://huggingface.co/datasets/s-emanuilov/rivers-qa-v4`

**Contents**:
- `river_qa_dataset.csv` (3.6MB) - 17,726 multiple-choice questions with canonical ordering
- `river_qa_dataset_shuffled.csv` (3.6MB) - Randomized answer positions (eliminates positional bias)

**Format**: Each question has 5 options with one correct answer, systematically generated from river abstracts

**Description**: Comprehensive evaluation dataset for testing factual grounding and hallucination detection. Questions probe specific numerical values, geographic relationships, and categorical properties. Ideal for benchmarking LLM factual accuracy in structured domains.

---

### 1.3 Knowledge Graph

**Repository**: `https://huggingface.co/datasets/s-emanuilov/rivers-knowledge-graph-v4`

**Contents**:
- `knowledge_graph.ttl` (RDF format, 118,047 triples)
- `worldmind_core.ttl` - Domain ontology (6 classes, 20+ properties)
- `worldmind_constraints.shacl.ttl` - SHACL validation shapes

**Ontology Classes**:
- River, GeographicFeature, State, County, Country, RiverSystem

**Constraint Types**:
- Elevation constraints (source > mouth)
- Positive value requirements (length, discharge)
- Geographic consistency rules
- Tributary type validation

**Description**: Formal knowledge graph implementing the licensing oracle architecture. RDF triples enable SPARQL querying and SHACL constraint validation for truth-constrained generation.

---

## 2. Fine-Tuned Models

### 2.1 Gemma-3-4B-Rivers-Factual

**Repository**: `https://huggingface.co/s-emanuilov/gemma-3-4b-rivers-factual`

**Base Model**: Google Gemma 3-4B-Instruct  
**Training Method**: LoRA (rank-16, 4-bit quantization)  
**Training Data**: 17,726 question-answer pairs with factual responses  
**Training Steps**: 100 steps at 2×10⁻⁴ learning rate  
**Evaluation Accuracy**: 8.5%

**Target Layers**: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

**Description**: Supervised fine-tuning variant trained to maximize factual recall. Results demonstrate that parameter optimization cannot reliably absorb factual knowledge across diverse question spaces—accuracy actually degraded compared to base model (16.7% → 8.5%).

---

### 2.2 Gemma-3-4B-Rivers-Abstain

**Repository**: `https://huggingface.co/s-emanuilov/gemma-3-4b-rivers-abstain`

**Base Model**: Google Gemma 3-4B-Instruct  
**Training Method**: LoRA (rank-16, 4-bit quantization)  
**Training Data**: 17,726 mixed responses (correct factual / "I don't know" for incorrect)  
**Training Steps**: 100 steps at 2×10⁻⁴ learning rate  
**Evaluation Metrics**:
- Answer Accuracy: 8.6%
- Abstention Precision: 56.7%
- Abstention Recall: 63.7%

**Description**: Supervised fine-tuning variant explicitly trained to abstain ("I don't know") when uncertain. Results show learned behavioral mimicry rather than genuine epistemic calibration—abstention precision barely exceeds random chance, demonstrating that statistical learning cannot encode principled epistemic boundaries.

---

## 3. Evaluation Results

### 3.1 Complete Evaluation Suite

**Repository**: `https://huggingface.co/datasets/s-emanuilov/rivers-evaluation-results-v4`

**Contents**:

#### Baseline Model Evaluations:
- `anthropic_claude-sonnet-4.5_results.jsonl` - 4,208 questions, 42.0% accuracy
- `google_gemini-2.5-flash-lite_results.jsonl` - 12,174 questions, 50.1% accuracy
- `google_gemma-3-4b-it_results.jsonl` - 7,839 questions, 16.7% accuracy

#### Fine-Tuned Model Evaluations:
- `gemma-3-4b-factual_results.jsonl` - 17,725 questions, 8.5% accuracy
- `gemma-3-4b-abstain_results.jsonl` - 17,725 questions, 8.6% accuracy
- `gemma-3-4b-abstain-wrong-only_results.jsonl` - Detailed abstention analysis

#### RAG System Evaluations:
- `rag_google_gemini-2.5-flash-lite_results.jsonl` - 23,781 questions, 89.5% accuracy
- `graph_rag_results.jsonl` - 16,626 questions, 89.1% accuracy with licensing validation

**Format**: JSONL with fields: question_id, question, correct_answer, model_response, is_correct, timestamp, (optional) retrieval_context, similarity_scores, claim_validations

**Description**: Complete evaluation outputs enabling reproducibility and failure mode analysis. Each JSONL record contains full question metadata, model response, correctness flag, and system-specific metrics (retrieval similarity for RAG, licensing decisions for Graph-RAG).

---

## 4. Code Repository

### 4.1 Complete Experimental Pipeline

**Repository**: `https://github.com/s-emanuilov/world-mind-poc-rivers`  
**License**: MIT

**Structure**:
```
world-mind-poc-rivers/
├── data/
│   ├── get_data.py              # DBpedia SPARQL extraction
│   ├── fill_missing_data.py     # LLM-based augmentation
│   └── generate_qa_dataset.py   # Question synthesis
├── graph_construction/
│   ├── build_graph.py           # CSV to RDF conversion
│   ├── worldmind_core.ttl       # Ontology definition
│   └── worldmind_constraints.shacl.ttl  # Validation shapes
├── evaluation/
│   ├── evaluate_llms.py         # Baseline LLM testing
│   └── compare_models.py        # Cross-model analysis
├── fine_tuning/
│   ├── train.ipynb              # LoRA training notebook
│   ├── evaluate.py              # Fine-tuned model evaluation
│   └── dataset_generation/      # Training data creation
├── rag/
│   ├── generate_embeddings.py   # multilingual-e5-large-instruct
│   ├── retrieval_system.py      # Cosine similarity search
│   └── evaluate_rag.py          # RAG pipeline evaluation
├── graph_rag/
│   ├── graph_retrieval.py       # Subgraph extraction
│   ├── extract_claims.py        # GLiNER claim extraction
│   ├── verify_claims.py         # SHACL validation oracle
│   └── evaluate_graph_rag.py    # Complete Graph-RAG pipeline
├── visualization/
│   └── generate_figures.py      # Publication-quality plots
├── requirements.txt
└── README.md
```

**Key Dependencies**:
- `rdflib` - RDF graph operations
- `pySHACL` - Constraint validation
- `transformers`, `torch` - LLM inference
- `unsloth` - Efficient LoRA training
- `gliner` - Claim extraction
- `openai` / `anthropic` - API clients (via OpenRouter)

**Description**: Complete, reproducible pipeline from raw data extraction through evaluation. Includes all scripts for data processing, knowledge graph construction, model training, RAG implementation, and evaluation. Jupyter notebooks provide interactive exploration of results.

---

## 5. Paper and Figures

### 5.1 Experimental Write-Up

**Repository**: Included in code repository under `paper/`

**Files**:
- `experiment_summary.md` - Complete experimental methodology and results (academic format)
- `graphs.md` - Python code for generating all figures
- `ARTIFACTS_SUMMARY.md` - This document

**Figures** (5 publication-ready visualizations):
1. Baseline model performance comparison
2. Fine-tuning results with abstention analysis
3. RAG vs Graph-RAG comparison
4. Complete experimental progression
5. Architectural capabilities matrix

All figures available as PNG (300 DPI) and PDF (vector) formats.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **River Entities** | 9,538 |
| **Knowledge Graph Triples** | 118,047 |
| **Question-Answer Pairs** | 17,726 |
| **Total Evaluations Conducted** | 111,578 |
| **Models Evaluated** | 8 (3 baseline + 2 fine-tuned + 3 systems) |
| **Best Baseline Accuracy** | 50.1% (Gemini 2.5 Flash Lite) |
| **RAG Accuracy** | 89.5% (embedding-based) |
| **Graph-RAG Accuracy** | 89.1% (with licensing oracle) |
| **Fine-Tuning Improvement** | -8.1 to -8.2 pp (degradation) |
| **RAG Improvement** | +39.4 pp over best baseline |

---

## Citation

If you use these artifacts in your research, please cite:

```bibtex
@article{emanuilov2025truthconstrained,
  title={Experimental Validation of Truth-Constrained Generation via Graph-Licensed Abstention},
  author={Emanuilov, Simeon and [Co-authors]},
  journal={[Journal/Conference]},
  year={2025},
  note={Datasets and models available at HuggingFace: s-emanuilov}
}
```

---

## Release Checklist

- [ ] Upload `rivers-knowledge-base-v4` to HuggingFace Datasets
- [ ] Upload `rivers-qa-v4` to HuggingFace Datasets
- [ ] Upload `rivers-knowledge-graph-v4` to HuggingFace Datasets
- [ ] Upload `rivers-evaluation-results-v4` to HuggingFace Datasets
- [ ] Upload `gemma-3-4b-rivers-factual` model to HuggingFace Models
- [ ] Upload `gemma-3-4b-rivers-abstain` model to HuggingFace Models
- [ ] Push code repository to GitHub: `s-emanuilov/world-mind-poc-rivers`
- [ ] Add MIT license to all repositories
- [ ] Create comprehensive README.md with setup instructions
- [ ] Add dataset cards describing data collection and intended use
- [ ] Add model cards describing training procedures and limitations
- [ ] Generate and commit all 5 figures (PNG + PDF)
- [ ] Add DOI references once published

---

## Contact

**Primary Author**: Simeon Emanuilov  
**HuggingFace**: [@s-emanuilov](https://huggingface.co/s-emanuilov)  
**GitHub**: [@s-emanuilov](https://github.com/s-emanuilov)

For questions about the artifacts or to report issues, please open an issue on the GitHub repository or contact via HuggingFace discussions.

---

**Last Updated**: October 28, 2025  
**Version**: 1.0  
**Status**: Ready for public release pending final review


