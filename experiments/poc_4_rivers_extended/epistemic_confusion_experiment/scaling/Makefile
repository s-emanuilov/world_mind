# Makefile for Scaled Epistemic Confusion Experiment
# Generates and evaluates 1500 cards (500 per type)

.PHONY: all clean cards eval-kg eval-graph-rag eval-all metrics report compare help

# Configuration
KG_PATH = ../../graph_rag/data/knowledge_graph.ttl
SHACL_PATH = ../../graph_rag/ontology/worldmind_constraints.shacl.ttl
PRED_URI = http://worldmind.ai/rivers-v4\#hasMouth
PRED_LABEL = mouth
NUM_PER_TYPE = 500

# Output paths
RESULTS_DIR = results
CARDS_FILE = $(RESULTS_DIR)/scaled_cards.jsonl
KG_RESULTS = $(RESULTS_DIR)/kg_results.jsonl
GRAPH_RAG_RESULTS = $(RESULTS_DIR)/graph_rag_results.jsonl
ALL_RESULTS = $(RESULTS_DIR)/all_results.jsonl
METRICS_FILE = $(RESULTS_DIR)/metrics.json
REPORT_FILE = $(RESULTS_DIR)/report.html
COMPARISON_FILE = $(RESULTS_DIR)/comparison.json

# Baseline paths for comparison
BASELINE_CARDS = ../results/context_cards.jsonl
BASELINE_METRICS = ../results/metrics.json

# Python interpreter
PYTHON = python3

# ========================================
# Main Targets
# ========================================

all: cards eval-all metrics report compare
	@echo ""
	@echo "======================================"
	@echo "Scaled Pipeline Complete!"
	@echo "======================================"
	@echo "Cards:      $(CARDS_FILE) (1500 cards)"
	@echo "Results:    $(ALL_RESULTS)"
	@echo "Metrics:    $(METRICS_FILE)"
	@echo "Report:     $(REPORT_FILE)"
	@echo "Comparison: $(COMPARISON_FILE)"
	@echo ""
	@echo "Open $(REPORT_FILE) to view results"
	@echo "Open $(COMPARISON_FILE) to see baseline comparison"
	@echo ""

help:
	@echo "Scaled Epistemic Confusion Experiment - Makefile Targets"
	@echo ""
	@echo "Primary targets:"
	@echo "  make all              - Run complete scaled pipeline (1500 cards)"
	@echo "  make cards            - Generate 1500 context cards (500 per type)"
	@echo "  make eval-kg          - Evaluate with KG oracle"
	@echo "  make eval-graph-rag   - Evaluate with Graph-RAG"
	@echo "  make eval-all         - Run all evaluations"
	@echo "  make metrics          - Compute abstention metrics"
	@echo "  make report           - Generate HTML report"
	@echo "  make compare          - Compare with baseline (800 cards)"
	@echo "  make clean            - Remove generated files"
	@echo ""
	@echo "Configuration:"
	@echo "  NUM_PER_TYPE = $(NUM_PER_TYPE)"
	@echo "  Total cards = $(shell echo $$(($(NUM_PER_TYPE) * 3)))"
	@echo ""

# ========================================
# Card Generation
# ========================================

cards: $(CARDS_FILE)

$(CARDS_FILE): ../cards/make_context_cards.py $(KG_PATH)
	@echo "Generating $(NUM_PER_TYPE) cards per type (1500 total)..."
	@mkdir -p $(RESULTS_DIR)
	$(PYTHON) ../cards/make_context_cards.py \
		--kg $(KG_PATH) \
		--pred "$(PRED_URI)" \
		--pred-label "$(PRED_LABEL)" \
		--num-per-type $(NUM_PER_TYPE) \
		--out $(CARDS_FILE) \
		--seed 42
	@echo "✓ Scaled cards generated: $(CARDS_FILE)"
	@wc -l $(CARDS_FILE)
	@echo "Distribution:"
	@grep '"label": "E"' $(CARDS_FILE) | wc -l | xargs -I {} echo "  E (Entailed):     {}"
	@grep '"label": "C"' $(CARDS_FILE) | wc -l | xargs -I {} echo "  C (Contradictory): {}"
	@grep '"label": "U"' $(CARDS_FILE) | wc -l | xargs -I {} echo "  U (Unknown):      {}"

# ========================================
# System Evaluation
# ========================================

eval-kg: $(KG_RESULTS)

$(KG_RESULTS): $(CARDS_FILE) ../eval/run_epistemic_tests.py
	@echo "Evaluating KG Oracle on 1500 cards..."
	$(PYTHON) ../eval/run_epistemic_tests.py \
		--cards $(CARDS_FILE) \
		--system kg \
		--out $(KG_RESULTS)
	@echo "✓ KG Oracle evaluation complete: $(KG_RESULTS)"

eval-graph-rag: $(GRAPH_RAG_RESULTS)

$(GRAPH_RAG_RESULTS): $(CARDS_FILE) ../eval/run_epistemic_tests.py $(KG_PATH)
	@echo "Evaluating Graph-RAG on 1500 cards..."
	$(PYTHON) ../eval/run_epistemic_tests.py \
		--cards $(CARDS_FILE) \
		--system graph_rag \
		--kg-path $(KG_PATH) \
		--shacl-path $(SHACL_PATH) \
		--out $(GRAPH_RAG_RESULTS)
	@echo "✓ Graph-RAG evaluation complete: $(GRAPH_RAG_RESULTS)"

eval-all: $(ALL_RESULTS)

$(ALL_RESULTS): $(KG_RESULTS) $(GRAPH_RAG_RESULTS)
	@echo "Merging evaluation results..."
	@cat $(KG_RESULTS) $(GRAPH_RAG_RESULTS) > $(ALL_RESULTS)
	@echo "✓ All results merged: $(ALL_RESULTS)"

# ========================================
# Metrics and Reporting
# ========================================

metrics: $(METRICS_FILE)

$(METRICS_FILE): $(ALL_RESULTS) ../eval/metrics_abstention.py
	@echo "Computing abstention metrics for scaled experiment..."
	$(PYTHON) ../eval/metrics_abstention.py \
		--results $(ALL_RESULTS) \
		--out $(METRICS_FILE) \
		--verbose
	@echo "✓ Metrics computed: $(METRICS_FILE)"

report: $(REPORT_FILE)

$(REPORT_FILE): $(ALL_RESULTS) $(METRICS_FILE) ../reporting/html_report.py
	@echo "Generating HTML report for scaled experiment..."
	$(PYTHON) ../reporting/html_report.py \
		--results $(ALL_RESULTS) \
		--metrics $(METRICS_FILE) \
		--out $(REPORT_FILE)
	@echo "✓ Report generated: $(REPORT_FILE)"

# ========================================
# Comparison Analysis
# ========================================

compare: $(COMPARISON_FILE)

$(COMPARISON_FILE): $(METRICS_FILE) $(BASELINE_METRICS)
	@echo "Comparing scaled experiment with baseline..."
	@$(PYTHON) -c "import json; \
		baseline = json.load(open('$(BASELINE_METRICS)')); \
		scaled = json.load(open('$(METRICS_FILE)')); \
		comparison = { \
			'baseline': {'cards': 800, 'metrics': baseline}, \
			'scaled': {'cards': 1500, 'metrics': scaled}, \
			'scale_factor': 1.875, \
			'deltas': {} \
		}; \
		for system in ['kg', 'graph_rag']: \
			if system in baseline and system in scaled: \
				comparison['deltas'][system] = {}; \
				for metric in ['AP', 'CVRR', 'FAR_NE', 'LA', 'overall_accuracy']: \
					if metric in baseline[system]['metrics'] and metric in scaled[system]['metrics']: \
						comparison['deltas'][system][metric] = scaled[system]['metrics'][metric] - baseline[system]['metrics'][metric]; \
		json.dump(comparison, open('$(COMPARISON_FILE)', 'w'), indent=2)" || echo "Warning: Comparison failed, check if baseline metrics exist"
	@echo "✓ Comparison generated: $(COMPARISON_FILE)"
	@echo ""
	@echo "=== Quick Comparison ==="
	@cat $(COMPARISON_FILE) 2>/dev/null | $(PYTHON) -m json.tool || echo "Comparison file not yet available"

# ========================================
# Utilities
# ========================================

clean:
	@echo "Cleaning scaled experiment files..."
	rm -rf $(RESULTS_DIR)
	@echo "✓ Clean complete"

stats:
	@echo "Scaled Experiment Statistics:"
	@echo ""
	@if [ -f $(CARDS_FILE) ]; then \
		echo "Generated Cards:"; \
		wc -l $(CARDS_FILE); \
		echo "  E (Entailed):     $$(grep '"label": "E"' $(CARDS_FILE) | wc -l)"; \
		echo "  C (Contradictory): $$(grep '"label": "C"' $(CARDS_FILE) | wc -l)"; \
		echo "  U (Unknown):      $$(grep '"label": "U"' $(CARDS_FILE) | wc -l)"; \
		echo ""; \
	fi
	@if [ -f $(METRICS_FILE) ]; then \
		echo "Systems evaluated:"; \
		cat $(METRICS_FILE) | jq -r 'keys[]' | sed 's/^/  - /'; \
		echo ""; \
		echo "Graph-RAG Metrics:"; \
		cat $(METRICS_FILE) | jq '.graph_rag.metrics' 2>/dev/null || echo "  Not yet computed"; \
	fi

config:
	@echo "Scaled Experiment Configuration:"
	@echo "  KG_PATH:       $(KG_PATH)"
	@echo "  SHACL_PATH:    $(SHACL_PATH)"
	@echo "  PRED_URI:      $(PRED_URI)"
	@echo "  NUM_PER_TYPE:  $(NUM_PER_TYPE)"
	@echo "  TOTAL CARDS:   $(shell echo $$(($(NUM_PER_TYPE) * 3)))"
	@echo "  SCALE FACTOR:  1.875× baseline"
	@echo ""
	@echo "Baseline for comparison:"
	@echo "  Cards:   800"
	@echo "  Metrics: $(BASELINE_METRICS)"

.DEFAULT_GOAL := help


