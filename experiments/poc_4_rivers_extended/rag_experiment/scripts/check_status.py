#!/usr/bin/env python3
"""
Quick status checker for RAG evaluation
Shows current progress without running the full evaluation.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_rag import RAGEvaluator

def main():
    """Show current evaluation status."""
    config_path = 'config/rag_config.json'
    model_name = "google/gemini-2.5-flash-lite"
    
    try:
        evaluator = RAGEvaluator(config_path, model_name)
        evaluator.show_status()
    except Exception as e:
        print(f"Error checking status: {e}")
        print("Make sure you're in the rag_experiment directory and have run the setup.")

if __name__ == "__main__":
    main()
