# HuggingFace Repository READMEs

This folder contains ready-to-upload README files for each HuggingFace repository that will be published as part of the Rivers experimental validation project.

## 📦 Repositories

### Datasets (4 repos)

1. **`README_rivers_knowledge_base.md`**
   - Repository: `s-emanuilov/rivers-knowledge-base`
   - Contents: 9,538 river entities with 21 attributes
   - Files: `raw_rivers.csv` + `raw_rivers_filled.csv`

2. **`README_rivers_qa.md`**
   - Repository: `s-emanuilov/rivers-qa`
   - Contents: 17,726 multiple-choice questions
   - Files: `river_qa_dataset.csv` + `river_qa_dataset_shuffled.csv`

3. **`README_rivers_knowledge_graph.md`**
   - Repository: `s-emanuilov/rivers-knowledge-graph`
   - Contents: 118,047 RDF triples + ontology + SHACL constraints
   - Files: `knowledge_graph.ttl` + `worldmind_core.ttl` + `worldmind_constraints.shacl.ttl`

4. **`README_rivers_evaluation_results.md`**
   - Repository: `s-emanuilov/rivers-evaluation-results`
   - Contents: 111,578 evaluation records across 8 systems
   - Files: Multiple JSONL files (baseline, fine-tuned, RAG evaluations)

### Models (2 repos)

5. **`README_gemma_3_4b_rivers_factual.md`**
   - Repository: `s-emanuilov/gemma-3-4b-rivers-factual`
   - Contents: LoRA fine-tuned model for factual recall
   - Performance: 8.5% accuracy (degradation from baseline)

6. **`README_gemma_3_4b_rivers_abstain.md`**
   - Repository: `s-emanuilov/gemma-3-4b-rivers-abstain`
   - Contents: LoRA fine-tuned model for abstention behavior
   - Performance: 8.6% accuracy, 56.7% abstention precision

## 🚀 Upload Instructions

### For Dataset Repositories

1. Go to https://huggingface.co/new-dataset
2. Create repository with the name (e.g., `rivers-knowledge-base`)
3. Copy the corresponding README content
4. Upload the data files mentioned in the README
5. Set license (CC BY-SA for data derived from DBpedia)

### For Model Repositories

1. Go to https://huggingface.co/new
2. Create repository with the name (e.g., `gemma-3-4b-rivers-factual`)
3. Copy the corresponding README content
4. Upload the LoRA adapter files
5. Set base model (google/gemma-3-4b-it)
6. Set license (Gemma license + MIT for adapters)

## 📋 Upload Checklist

- [ ] Create dataset: `rivers-knowledge-base`
  - [ ] Upload `raw_rivers.csv`
  - [ ] Upload `raw_rivers_filled.csv`
  - [ ] Add README from `README_rivers_knowledge_base.md`
  
- [ ] Create dataset: `rivers-qa`
  - [ ] Upload `river_qa_dataset.csv`
  - [ ] Upload `river_qa_dataset_shuffled.csv`
  - [ ] Add README from `README_rivers_qa.md`
  
- [ ] Create dataset: `rivers-knowledge-graph`
  - [ ] Upload `knowledge_graph.ttl`
  - [ ] Upload `worldmind_core.ttl`
  - [ ] Upload `worldmind_constraints.shacl.ttl`
  - [ ] Add README from `README_rivers_knowledge_graph.md`
  
- [ ] Create dataset: `rivers-evaluation-results`
  - [ ] Upload all JSONL evaluation files
  - [ ] Add README from `README_rivers_evaluation_results.md`
  
- [ ] Create model: `gemma-3-4b-rivers-factual`
  - [ ] Upload LoRA adapter files
  - [ ] Add README from `README_gemma_3_4b_rivers_factual.md`
  - [ ] Tag base model: `google/gemma-3-4b-it`
  
- [ ] Create model: `gemma-3-4b-rivers-abstain`
  - [ ] Upload LoRA adapter files
  - [ ] Add README from `README_gemma_3_4b_rivers_abstain.md`
  - [ ] Tag base model: `google/gemma-3-4b-it`

## 📝 Notes

- All URLs use the base format without versioning: `s-emanuilov/<repo-name>`
- READMEs include usage examples, citations, and licensing information
- Each README is 5-10 sentences with detailed context
- All artifacts cross-reference each other for discoverability

## 🔗 Final URLs

After publishing, repositories will be accessible at:

**Datasets:**
- https://huggingface.co/datasets/s-emanuilov/rivers-knowledge-base
- https://huggingface.co/datasets/s-emanuilov/rivers-qa
- https://huggingface.co/datasets/s-emanuilov/rivers-knowledge-graph
- https://huggingface.co/datasets/s-emanuilov/rivers-evaluation-results

**Models:**
- https://huggingface.co/s-emanuilov/gemma-3-4b-rivers-factual
- https://huggingface.co/s-emanuilov/gemma-3-4b-rivers-abstain




