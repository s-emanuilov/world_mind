#!/usr/bin/env python3
"""
Main execution script for RAG experiment
Runs the complete RAG pipeline: document processing -> embedding generation -> evaluation -> comparison
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_script(script_path: str, description: str):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              cwd=os.path.dirname(os.path.abspath(__file__)),
                              check=True, 
                              capture_output=True, 
                              text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Errors: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def check_config():
    """Check if configuration file exists."""
    config_path = "config/rag_config.json"
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found!")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check if data files exist
    questions_path = config['data_paths']['questions']
    documents_path = config['data_paths']['documents']
    
    if not os.path.exists(questions_path):
        print(f"Error: Questions file {questions_path} not found!")
        return False
    
    if not os.path.exists(documents_path):
        print(f"Error: Documents file {documents_path} not found!")
        return False
    
    print("Configuration check passed!")
    return True

def main():
    """Main execution function."""
    print("RAG Experiment Pipeline")
    print("======================")
    
    # Check configuration
    if not check_config():
        return
    
    # Define pipeline steps
    steps = [
        ("scripts/process_documents.py", "Document Processing and Chunking"),
        ("scripts/generate_embeddings.py", "Embedding Generation"),
        ("scripts/evaluate_rag.py", "RAG Evaluation"),
        ("scripts/compare_results.py", "Results Comparison")
    ]
    
    # Run each step
    for script_path, description in steps:
        success = run_script(script_path, description)
        if not success:
            print(f"\nPipeline stopped at: {description}")
            print("Please fix the error and run again.")
            return
    
    print(f"\n{'='*60}")
    print("RAG Experiment Pipeline Completed Successfully!")
    print(f"{'='*60}")
    
    # Print summary of generated files
    print("\nGenerated Files:")
    print("- data/river_chunks.json: Processed document chunks")
    print("- embeddings/river_embeddings.npy: Document embeddings")
    print("- embeddings/chunk_metadata.json: Chunk metadata")
    print("- results/rag_*_results.jsonl: RAG evaluation results")
    print("- results/analysis/: Comparison analysis reports")

if __name__ == "__main__":
    main()
