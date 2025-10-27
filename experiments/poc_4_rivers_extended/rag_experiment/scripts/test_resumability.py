#!/usr/bin/env python3
"""
Test script to verify RAG evaluation resumability and accuracy tracking
"""

import json
import os
import tempfile
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_rag import RAGEvaluator

def test_resumability():
    """Test that the evaluation correctly resumes from existing results."""
    print("Testing RAG evaluation resumability...")
    
    # Create a temporary results file with some test data
    test_results = [
        {
            'question_id': 'test_1',
            'question': 'Test question 1',
            'answers': ['A', 'B', 'C', 'D', 'E'],
            'correct_answer_index': 0,
            'correct_answer': 'A',
            'llm_response': 'A',
            'is_correct': True,
            'context': 'Test context',
            'retrieval_info': {'top_similarity': 0.8},
            'timestamp': '2024-01-01T00:00:00'
        },
        {
            'question_id': 'test_2',
            'question': 'Test question 2',
            'answers': ['A', 'B', 'C', 'D', 'E'],
            'correct_answer_index': 1,
            'correct_answer': 'B',
            'llm_response': 'C',
            'is_correct': False,
            'context': 'Test context',
            'retrieval_info': {'top_similarity': 0.7},
            'timestamp': '2024-01-01T00:00:00'
        }
    ]
    
    # Create temporary directory and files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config = {
            "embedding_model": "intfloat/multilingual-e5-large-instruct",
            "data_paths": {
                "questions": "dummy.csv",
                "documents": "dummy.csv"
            },
            "output_paths": {
                "chunks": "dummy.json",
                "embeddings": "dummy.npy",
                "metadata": "dummy.json",
                "results": "dummy.jsonl"
            }
        }
        
        config_path = os.path.join(temp_dir, "test_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        # Create test results file
        results_file = os.path.join(temp_dir, "test_results.jsonl")
        with open(results_file, 'w') as f:
            for result in test_results:
                f.write(json.dumps(result) + '\n')
        
        # Test the evaluator (without actually running evaluation)
        try:
            # Mock the retrieval system to avoid loading embeddings
            class MockRetrievalSystem:
                def __init__(self, config_path):
                    pass
            
            # Replace the retrieval system import
            import evaluate_rag
            evaluate_rag.RetrievalSystem = MockRetrievalSystem
            
            evaluator = RAGEvaluator(config_path, "test-model")
            evaluator.results_file = results_file
            
            # Test get_completed_questions
            completed = evaluator.get_completed_questions()
            assert len(completed) == 2, f"Expected 2 completed questions, got {len(completed)}"
            assert 'test_1' in completed, "test_1 not found in completed questions"
            assert 'test_2' in completed, "test_2 not found in completed questions"
            
            # Test get_current_accuracy
            correct, total, accuracy = evaluator.get_current_accuracy()
            assert correct == 1, f"Expected 1 correct answer, got {correct}"
            assert total == 2, f"Expected 2 total questions, got {total}"
            assert accuracy == 0.5, f"Expected 0.5 accuracy, got {accuracy}"
            
            print("✓ Resumability test passed!")
            print(f"  Completed questions: {len(completed)}")
            print(f"  Accuracy: {correct}/{total} = {accuracy:.2%}")
            
        except Exception as e:
            print(f"✗ Resumability test failed: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("RAG Evaluation Resumability Test")
    print("=" * 40)
    
    success = test_resumability()
    
    if success:
        print("\n✓ All tests passed!")
        print("The RAG evaluation system correctly handles resumability and accuracy tracking.")
    else:
        print("\n✗ Tests failed!")
        print("Please check the implementation.")

if __name__ == "__main__":
    main()
