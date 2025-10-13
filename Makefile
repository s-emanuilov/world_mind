.PHONY: all data build validate test clean

# Default command to run the main steps
all: data build validate test

# Fetches the raw data from DBpedia
data:
	python -m scripts.get_data

# Builds the knowledge graph from the raw data
build:
	python -m scripts.build_graph

# Validates the knowledge graph against SHACL constraints
validate:
	python -m scripts.validate_graph

# Runs the canonical prompt suite for evaluation
test:
	python -m scripts.eval_prompts

# Removes generated artifacts
clean:
	rm -rf artifacts/* data/raw_philosophers.csv data/knowledge_graph.ttl