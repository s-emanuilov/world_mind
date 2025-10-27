#!/usr/bin/env python3
"""
Test script to verify RAG experiment setup
Tests individual components without running the full pipeline.
"""

import json
import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"✗ PyTorch: {e}")
        return False
    
    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"✗ Transformers: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    try:
        import sklearn
        print(f"✓ Scikit-learn {sklearn.__version__}")
    except ImportError as e:
        print(f"✗ Scikit-learn: {e}")
        return False
    
    return True

def test_config():
    """Test configuration file."""
    print("\nTesting configuration...")
    
    config_path = "config/rag_config.json"
    if not os.path.exists(config_path):
        print(f"✗ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("✓ Configuration file loaded successfully")
        
        # Check required fields
        required_fields = ['embedding_model', 'data_paths', 'output_paths']
        for field in required_fields:
            if field not in config:
                print(f"✗ Missing required field: {field}")
                return False
        
        print("✓ All required configuration fields present")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        return False

def test_data_files():
    """Test if data files exist."""
    print("\nTesting data files...")
    
    config_path = "config/rag_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    questions_path = config['data_paths']['questions']
    documents_path = config['data_paths']['documents']
    
    if os.path.exists(questions_path):
        print(f"✓ Questions file found: {questions_path}")
    else:
        print(f"✗ Questions file not found: {questions_path}")
        return False
    
    if os.path.exists(documents_path):
        print(f"✓ Documents file found: {documents_path}")
    else:
        print(f"✗ Documents file not found: {documents_path}")
        return False
    
    return True

def test_model_download():
    """Test if embedding model can be loaded."""
    print("\nTesting embedding model...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        model_name = "intfloat/multilingual-e5-large-instruct"
        print(f"Loading model: {model_name}")
        
        # Test tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("✓ Tokenizer loaded successfully")
        
        # Test model (this might take a while)
        print("Loading model (this may take a moment)...")
        model = AutoModel.from_pretrained(model_name)
        print("✓ Model loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False

def test_api_key():
    """Test if OpenRouter API key is available."""
    print("\nTesting API key...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            print("✓ OpenRouter API key found")
            return True
        else:
            print("✗ OpenRouter API key not found in environment")
            print("  Please set OPENROUTER_API_KEY in your .env file")
            return False
            
    except ImportError:
        print("✗ python-dotenv not installed")
        return False

def main():
    """Run all tests."""
    print("RAG Experiment Setup Test")
    print("========================")
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Data Files", test_data_files),
        ("Embedding Model", test_model_download),
        ("API Key", test_api_key)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*40}")
    print("Test Summary:")
    print(f"{'='*40}")
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n✓ All tests passed! RAG experiment setup is ready.")
    else:
        print(f"\n✗ {len(results) - passed} test(s) failed. Please fix the issues before running the experiment.")

if __name__ == "__main__":
    main()
