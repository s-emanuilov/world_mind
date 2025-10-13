.PHONY: all data build validate prompts test clean

# Default command to run the main steps
all: data build validate test

# Fetches the raw data from DBpedia
data:
	python scripts/get_data.py

# Builds the knowledge graph from the raw data
build:
	python scripts/build_graph.py

# Validates the knowledge graph against SHACL constraints
validate:
	python scripts/validate_graph.py

# Generates test prompts from actual graph data
prompts:
	python scripts/generate_prompts.py

# Runs the canonical prompt suite for evaluation
test:
	python scripts/eval_prompts.py

# Removes generated artifacts
clean:
	rm -rf artifacts/* data/raw_battles.csv data/knowledge_graph.ttl data/prompt_suite.json

