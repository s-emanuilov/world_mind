#!/bin/bash
# Balanced test across all epistemic labels (E, C, U)

cd "$(dirname "$0")"

echo "====================================================================="
echo "LLM Epistemic Confusion - Balanced Test"
echo "====================================================================="
echo ""
echo "Testing on 30 cards (10 Entailed, 10 Contradictory, 10 Unknown)"
echo "This will show abstention behavior on C and U cards"
echo ""

# Check API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "ERROR: OPENROUTER_API_KEY not set"
    exit 1
fi

echo "API Key: ${OPENROUTER_API_KEY:0:20}... ✓"
echo ""

mkdir -p results

# Create a balanced sample (cards 0-9 E, 200-209 C, 400-409 U)
echo "Creating balanced sample..."
cd ..
{
    head -10 results/context_cards.jsonl  # E cards
    tail -n +201 results/context_cards.jsonl | head -10  # C cards  
    tail -n +401 results/context_cards.jsonl | head -10  # U cards
} > llm_test/results/balanced_sample.jsonl

cd llm_test

echo "Sample created: 30 cards (10 E + 10 C + 10 U)"
echo ""

# Test Claude
echo "====================================================================="
echo "Test 1/2: Claude 3.5 Sonnet (Balanced)"
echo "====================================================================="
python run_llm_test.py \
    --cards results/balanced_sample.jsonl \
    --model "anthropic/claude-3.5-sonnet" \
    --name "claude-3.5-sonnet" \
    --max 30 \
    --out results/claude_balanced.jsonl

echo ""

# Test GPT-4
echo "====================================================================="
echo "Test 2/2: GPT-4 (Balanced)"
echo "====================================================================="
python run_llm_test.py \
    --cards results/balanced_sample.jsonl \
    --model "openai/gpt-4" \
    --name "gpt-4" \
    --max 30 \
    --out results/gpt4_balanced.jsonl

echo ""

# Merge and compute metrics
cat results/claude_balanced.jsonl results/gpt4_balanced.jsonl > results/all_balanced.jsonl

echo "====================================================================="
echo "Computing Metrics"
echo "====================================================================="
cd ..
python eval/metrics_abstention.py \
    --results llm_test/results/all_balanced.jsonl \
    --out llm_test/results/balanced_metrics.json \
    --verbose

echo ""
echo "====================================================================="
echo "Summary Comparison"
echo "====================================================================="
echo ""
echo "Graph-RAG (from main experiment, 800 cards):"
echo "  AP:     1.000 (perfect abstention precision)"
echo "  CVRR:   0.500 (catches explicit contradictions)"  
echo "  FAR-NE: 0.333 (low false answer rate)"
echo "  LA:     1.000 (perfect on entailed)"
echo ""
echo "Real LLMs (30 cards, see above for detailed results):"
echo "  Check results/balanced_metrics.json"
echo ""


