.PHONY: all data build validate generate-answers eval-answers clean

# Default command to run the main steps
all: data build validate generate-answers eval-answers

# Fetches the raw data from DBpedia
data:
	python scripts/get_data.py

# Builds the knowledge graph from the raw data
build:
	python scripts/build_graph.py

# Validates the knowledge graph against SHACL constraints
validate:
	python scripts/validate_graph.py

# Generates test answers from actual graph data
generate-answers:
	python scripts/generate_prompts.py

# Runs the canonical answer suite for evaluation
eval-answers:
	python scripts/eval_answers.py

# Removes generated artifacts
clean:
	rm -rf artifacts/* data/raw_battles.csv data/knowledge_graph.ttl data/prompt_suite.json

