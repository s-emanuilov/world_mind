.PHONY: data build validate evaluate clean compare help

# Default directory
DIR = .

help:
	@echo "Graph-RAG Experiment Makefile"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  data       - Build knowledge graph from CSV"
	@echo "  build      - Alias for 'data'"
	@echo "  validate   - Validate graph against SHACL constraints"
	@echo "  evaluate   - Run Graph-RAG evaluation"
	@echo "  compare    - Compare with baseline RAG"
	@echo "  clean      - Remove generated files"
	@echo "  all        - Run complete pipeline"

data:
	@echo "Building knowledge graph..."
	python scripts/build_graph.py

build: data

validate:
	@echo "Validating graph against SHACL constraints..."
	python scripts/validate_graph.py

evaluate:
	@echo "Running Graph-RAG evaluation..."
	python scripts/evaluate_graph_rag.py --max-questions 100

compare:
	@echo "Comparing Graph-RAG with baseline RAG..."
	python scripts/compare_results.py

clean:
	@echo "Cleaning generated files..."
	rm -f data/knowledge_graph.ttl
	rm -f results/*.json results/*.jsonl

all: data validate evaluate
