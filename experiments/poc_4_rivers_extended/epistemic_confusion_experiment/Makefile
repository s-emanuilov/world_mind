# Makefile for Epistemic Confusion Experiment
# Automates the pipeline for generating context cards, evaluating systems, and producing reports

.PHONY: all clean cards eval-kg eval-graph-rag eval-all metrics report help

# Configuration
KG_PATH = ../graph_rag/data/knowledge_graph.ttl
SHACL_PATH = ../graph_rag/ontology/worldmind_constraints.shacl.ttl
PRED_URI = http://worldmind.ai/rivers-v4\#hasMouth
PRED_LABEL = mouth
NUM_PER_TYPE = 200

# Output paths
RESULTS_DIR = results
CARDS_FILE = $(RESULTS_DIR)/context_cards.jsonl
NEAR_MISS_FILE = $(RESULTS_DIR)/near_miss_cards.jsonl
KG_RESULTS = $(RESULTS_DIR)/kg_results.jsonl
GRAPH_RAG_RESULTS = $(RESULTS_DIR)/graph_rag_results.jsonl
ALL_RESULTS = $(RESULTS_DIR)/all_results.jsonl
METRICS_FILE = $(RESULTS_DIR)/metrics.json
REPORT_FILE = $(RESULTS_DIR)/report.html

# Python interpreter
PYTHON = python3

# ========================================
# Main Targets
# ========================================

all: cards eval-all metrics report
	@echo ""
	@echo "======================================"
	@echo "Pipeline complete!"
	@echo "======================================"
	@echo "Cards:   $(CARDS_FILE)"
	@echo "Results: $(ALL_RESULTS)"
	@echo "Metrics: $(METRICS_FILE)"
	@echo "Report:  $(REPORT_FILE)"
	@echo ""
	@echo "Open $(REPORT_FILE) in your browser to view results."
	@echo ""

help:
	@echo "Epistemic Confusion Experiment - Makefile Targets"
	@echo ""
	@echo "Primary targets:"
	@echo "  make all              - Run complete pipeline (cards → eval → metrics → report)"
	@echo "  make cards            - Generate context cards (E/C/U labeled)"
	@echo "  make eval-kg          - Evaluate with KG oracle (deterministic)"
	@echo "  make eval-graph-rag   - Evaluate with Graph-RAG system"
	@echo "  make eval-all         - Run all evaluations"
	@echo "  make metrics          - Compute abstention metrics"
	@echo "  make report           - Generate HTML report"
	@echo "  make near-miss        - Generate adversarial near-miss cases"
	@echo "  make clean            - Remove all generated files"
	@echo ""
	@echo "Configuration:"
	@echo "  KG_PATH = $(KG_PATH)"
	@echo "  PRED_URI = $(PRED_URI)"
	@echo "  PRED_LABEL = $(PRED_LABEL)"
	@echo "  NUM_PER_TYPE = $(NUM_PER_TYPE)"
	@echo ""

# ========================================
# Card Generation
# ========================================

cards: $(CARDS_FILE)

$(CARDS_FILE): cards/make_context_cards.py $(KG_PATH)
	@echo "Generating context cards..."
	@mkdir -p $(RESULTS_DIR)
	$(PYTHON) cards/make_context_cards.py \
		--kg $(KG_PATH) \
		--pred "$(PRED_URI)" \
		--pred-label "$(PRED_LABEL)" \
		--num-per-type $(NUM_PER_TYPE) \
		--out $(CARDS_FILE) \
		--seed 1337
	@echo "✓ Cards generated: $(CARDS_FILE)"

near-miss: $(NEAR_MISS_FILE)

$(NEAR_MISS_FILE): adversarial/make_near_miss.py $(KG_PATH)
	@echo "Generating near-miss adversarial cards..."
	@mkdir -p $(RESULTS_DIR)
	$(PYTHON) adversarial/make_near_miss.py \
		--kg $(KG_PATH) \
		--pred "$(PRED_URI)" \
		--pred-label "$(PRED_LABEL)" \
		--num 500 \
		--out $(NEAR_MISS_FILE) \
		--seed 2027
	@echo "✓ Near-miss cards generated: $(NEAR_MISS_FILE)"

# ========================================
# System Evaluation
# ========================================

eval-kg: $(KG_RESULTS)

$(KG_RESULTS): $(CARDS_FILE) eval/run_epistemic_tests.py
	@echo "Evaluating with KG Oracle (deterministic)..."
	$(PYTHON) eval/run_epistemic_tests.py \
		--cards $(CARDS_FILE) \
		--system kg \
		--out $(KG_RESULTS)
	@echo "✓ KG Oracle evaluation complete: $(KG_RESULTS)"

eval-graph-rag: $(GRAPH_RAG_RESULTS)

$(GRAPH_RAG_RESULTS): $(CARDS_FILE) eval/run_epistemic_tests.py $(KG_PATH)
	@echo "Evaluating with Graph-RAG (licensing oracle)..."
	$(PYTHON) eval/run_epistemic_tests.py \
		--cards $(CARDS_FILE) \
		--system graph_rag \
		--kg-path $(KG_PATH) \
		--shacl-path $(SHACL_PATH) \
		--out $(GRAPH_RAG_RESULTS)
	@echo "✓ Graph-RAG evaluation complete: $(GRAPH_RAG_RESULTS)"

eval-all: $(ALL_RESULTS)

$(ALL_RESULTS): $(KG_RESULTS) $(GRAPH_RAG_RESULTS)
	@echo "Merging all evaluation results..."
	@cat $(KG_RESULTS) $(GRAPH_RAG_RESULTS) > $(ALL_RESULTS)
	@echo "✓ All results merged: $(ALL_RESULTS)"

# ========================================
# Metrics and Reporting
# ========================================

metrics: $(METRICS_FILE)

$(METRICS_FILE): $(ALL_RESULTS) eval/metrics_abstention.py
	@echo "Computing abstention metrics..."
	$(PYTHON) eval/metrics_abstention.py \
		--results $(ALL_RESULTS) \
		--out $(METRICS_FILE) \
		--verbose
	@echo "✓ Metrics computed: $(METRICS_FILE)"

report: $(REPORT_FILE)

$(REPORT_FILE): $(ALL_RESULTS) $(METRICS_FILE) reporting/html_report.py
	@echo "Generating HTML report..."
	$(PYTHON) reporting/html_report.py \
		--results $(ALL_RESULTS) \
		--metrics $(METRICS_FILE) \
		--out $(REPORT_FILE)
	@echo "✓ Report generated: $(REPORT_FILE)"
	@echo ""
	@echo "Open in browser: file://$(shell pwd)/$(REPORT_FILE)"

# ========================================
# Utilities
# ========================================

clean:
	@echo "Cleaning generated files..."
	rm -rf $(RESULTS_DIR)
	@echo "✓ Clean complete"

# Show current configuration
config:
	@echo "Current Configuration:"
	@echo "  KG_PATH:       $(KG_PATH)"
	@echo "  SHACL_PATH:    $(SHACL_PATH)"
	@echo "  PRED_URI:      $(PRED_URI)"
	@echo "  PRED_LABEL:    $(PRED_LABEL)"
	@echo "  NUM_PER_TYPE:  $(NUM_PER_TYPE)"
	@echo "  RESULTS_DIR:   $(RESULTS_DIR)"

# Quick test with small number of cards
test: NUM_PER_TYPE=10
test: clean all
	@echo "Test run complete with $(NUM_PER_TYPE) cards per type"

# Alternative predicates

eval-tributary:
	@$(MAKE) clean
	@$(MAKE) all PRED_URI="http://worldmind.ai/rivers-v4\#hasTributary" PRED_LABEL="tributary"

eval-source:
	@$(MAKE) clean
	@$(MAKE) all PRED_URI="http://worldmind.ai/rivers-v4\#hasSource" PRED_LABEL="source"

# ========================================
# Development helpers
# ========================================

lint:
	@echo "Running linters..."
	@find . -name "*.py" -type f | xargs python3 -m pylint --errors-only

format:
	@echo "Formatting Python files..."
	@find . -name "*.py" -type f | xargs python3 -m black

# Show statistics about generated files
stats:
	@echo "File Statistics:"
	@echo ""
	@if [ -f $(CARDS_FILE) ]; then \
		echo "Context Cards:"; \
		wc -l $(CARDS_FILE); \
		echo "  E (Entailed):     $$(grep '"label": "E"' $(CARDS_FILE) | wc -l)"; \
		echo "  C (Contradictory): $$(grep '"label": "C"' $(CARDS_FILE) | wc -l)"; \
		echo "  U (Unknown):      $$(grep '"label": "U"' $(CARDS_FILE) | wc -l)"; \
		echo ""; \
	fi
	@if [ -f $(ALL_RESULTS) ]; then \
		echo "Evaluation Results:"; \
		wc -l $(ALL_RESULTS); \
		echo "  Systems: $$(jq -r .system $(ALL_RESULTS) | sort -u | tr '\n' ' ')"; \
		echo ""; \
	fi
	@if [ -f $(METRICS_FILE) ]; then \
		echo "Metrics computed for: $$(jq -r 'keys[]' $(METRICS_FILE) | tr '\n' ' ')"; \
	fi

.DEFAULT_GOAL := help


