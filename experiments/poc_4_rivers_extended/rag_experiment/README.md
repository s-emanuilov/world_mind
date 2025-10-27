# RAG Experiment for Rivers Q&A Dataset

This experiment implements a Retrieval-Augmented Generation (RAG) system for answering questions about US rivers and waterways.

## Structure

- `data/` - Processed datasets and document chunks
- `embeddings/` - Generated embeddings and vector store
- `scripts/` - Core RAG implementation scripts
- `results/` - Evaluation results and analysis
- `config/` - Configuration files

## Data Sources

- **Questions**: `river_qa_dataset_shuffled.csv` - Multiple choice questions about rivers
- **Knowledge Base**: `raw_rivers_filled.csv` - River documents with abstracts and metadata

## Embedding Model

Using `intfloat/multilingual-e5-large-instruct` for generating embeddings:
- Model: multilingual-e5-large-instruct
- Embedding dimension: 1024
- Max context: 512 tokens
- Supports instruction-based embedding for better retrieval

## RAG Pipeline

1. **Document Processing**: Extract and chunk river information from CSV
2. **Embedding Generation**: Create embeddings for document chunks
3. **Question Embedding**: Generate embeddings for questions with task instructions
4. **Retrieval**: Find most relevant document chunks using cosine similarity
5. **Generation**: Use retrieved context to answer questions
6. **Evaluation**: Compare RAG performance against direct LLM evaluation

## Usage

```bash
# Generate embeddings
python scripts/generate_embeddings.py

# Run RAG evaluation
python scripts/evaluate_rag.py

# Check current status without running evaluation
python scripts/evaluate_rag.py --status
# or
python scripts/check_status.py

# Compare with direct LLM results
python scripts/compare_results.py
```

## Real-time Progress Tracking

The RAG evaluation now provides real-time accuracy updates:

- **Resumability**: Automatically resumes from where it left off
- **Live Accuracy**: Shows running accuracy after each question
- **Progress Updates**: Displays progress every 10 questions
- **Status Checking**: Check current progress without running evaluation

Example output:
```
Starting RAG evaluation with google/gemini-2.5-flash-lite
Already completed: 150 questions
Current accuracy: 120/150 = 80.00%
============================================================
Processing river_123_4 (Mississippi River)...
  Response: C, Correct: True, Similarity: 0.856
  Running Accuracy: 121/151 = 80.13%
  Progress: 10 new questions processed | Total: 160 | Accuracy: 80.00%
```
