#!/bin/bash
# Quick test script for LLM epistemic confusion evaluation

cd "$(dirname "$0")"

echo "====================================================================="
echo "LLM Epistemic Confusion Quick Test"
echo "====================================================================="
echo ""
echo "This will test real LLMs (Claude and GPT-4) on 20 context cards each"
echo "to compare against Graph-RAG's performance (AP=1.0)"
echo ""
echo "Estimated cost: ~$0.10-0.20"
echo "Estimated time: ~2-3 minutes"
echo ""

# Check API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "ERROR: OPENROUTER_API_KEY not set"
    echo ""
    echo "Set it with:"
    echo "export OPENROUTER_API_KEY=your_key_here"
    exit 1
fi

echo "API Key: ${OPENROUTER_API_KEY:0:20}... ✓"
echo ""

# Create results directory
mkdir -p results

# Test Claude 3.5 Sonnet (20 cards)
echo "====================================================================="
echo "Test 1/2: Claude 3.5 Sonnet"
echo "====================================================================="
python run_llm_test.py \
    --cards ../results/context_cards.jsonl \
    --model "anthropic/claude-3.5-sonnet" \
    --name "claude-3.5-sonnet" \
    --max 20 \
    --out results/claude_test.jsonl

echo ""
echo ""

# Test GPT-4 (20 cards)
echo "====================================================================="
echo "Test 2/2: GPT-4"
echo "====================================================================="
python run_llm_test.py \
    --cards ../results/context_cards.jsonl \
    --model "openai/gpt-4" \
    --name "gpt-4" \
    --max 20 \
    --out results/gpt4_test.jsonl

echo ""
echo ""

# Merge results
echo "====================================================================="
echo "Merging Results"
echo "====================================================================="
cat results/claude_test.jsonl results/gpt4_test.jsonl > results/all_llm_test.jsonl
echo "Merged results: results/all_llm_test.jsonl"

# Compute metrics
echo ""
echo "Computing metrics..."
cd ..
python eval/metrics_abstention.py \
    --results llm_test/results/all_llm_test.jsonl \
    --out llm_test/results/llm_metrics.json \
    --verbose

echo ""
echo "====================================================================="
echo "Test Complete!"
echo "====================================================================="
echo ""
echo "Results:"
echo "  - results/claude_test.jsonl"
echo "  - results/gpt4_test.jsonl"
echo "  - results/llm_metrics.json"
echo ""
echo "Compare with Graph-RAG (AP=1.0, LA=1.0, FAR-NE=0.333)"
echo ""


