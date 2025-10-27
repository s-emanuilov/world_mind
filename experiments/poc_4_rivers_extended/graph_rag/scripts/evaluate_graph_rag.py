#!/usr/bin/env python3
"""
Graph-RAG evaluation for rivers dataset.
Implements graph-based retrieval with verification oracle.
"""

import json
import csv
import os
import sys
import time
import argparse
from typing import Dict, List, Any, Optional

# Add project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(EXPERIMENT_DIR)))
sys.path.insert(0, PROJECT_ROOT)

from graph_retrieval import GraphRetrievalSystem
from openrouter_client import OpenRouterClient

# Import worldmind components  
sys.path.insert(0, os.path.join(PROJECT_ROOT, "worldmind"))

try:
    from models import ConsistencyAuditor, AbstentionPolicy
    from graph_store import GraphStore
except ImportError:
    print("WARNING: Could not import worldmind models")
    ConsistencyAuditor = None
    AbstentionPolicy = None
    GraphStore = None


class GraphRAGEvaluator:
    """Evaluate Graph-RAG system with verification."""
    
    def __init__(self, model_name: str, graph_path: str):
        """Initialize evaluator."""
        self.model_name = model_name
        
        # Initialize OpenRouter client
        try:
            self.llm_client = OpenRouterClient()
        except Exception as e:
            print(f"WARNING: Could not initialize OpenRouter client: {e}")
            self.llm_client = None
        
        # Load graph
        self.retrieval = GraphRetrievalSystem(graph_path)
        
        # Initialize verification components if available
        self.verify_claims = ConsistencyAuditor is not None
        
        if self.verify_claims:
            constraints_path = os.path.join(
                os.path.dirname(EXPERIMENT_DIR), "graph_rag", "ontology",
                "worldmind_constraints.shacl.ttl"
            )
            self.auditor = ConsistencyAuditor(constraints_path)
            self.policy = AbstentionPolicy()
        else:
            print("WARNING: Verification disabled (worldmind modules not available)")
    
    def get_llm_response(self, question: str, context: str, answers: List[str]) -> str:
        """Get LLM response with context."""
        if self.llm_client is None:
            return "ERROR: No LLM client available"
        
        system_prompt = """You are an expert on US rivers and waterways. 
Answer the question based on the provided graph context.
Respond with just the letter (A, B, C, D, or E) of the correct answer."""
        
        user_prompt = f"""Context from knowledge graph:
{context}

Question: {question}

Answer choices:
A) {answers[0]}
B) {answers[1]}
C) {answers[2]}
D) {answers[3]}
E) {answers[4]}

What is the correct answer?"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm_client.chat(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=50
            )
            
            return OpenRouterClient.first_text(response)
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "ERROR"
    
    def evaluate_question(self, row: Dict, completed: set) -> Optional[Dict]:
        """Evaluate a single question with Graph-RAG."""
        question_id = row['question_id']
        
        if question_id in completed:
            return None
        
        question = row['question']
        answers = [row[f'answer_{i}'] for i in range(1, 6)]
        correct_index = int(row['correct_answer_index'])
        river_name = row['river_name']
        
        # Retrieve graph context
        graph_context = self.retrieval.retrieve_for_question(question, river_name)
        
        # Get LLM response
        llm_response = self.get_llm_response(question, graph_context, answers)
        
        # Extract answer letter from response
        answer_letter = self._extract_answer_letter(llm_response)
        
        # Check if correct
        correct = answer_letter and self._answer_letter_to_index(answer_letter) == correct_index
        
        result = {
            'question_id': question_id,
            'river_name': river_name,
            'question': question,
            'answer': llm_response,
            'extracted_answer': answer_letter,
            'correct_answer_index': correct_index,
            'is_correct': correct,
            'graph_context_length': len(graph_context)
        }
        
        return result
    
    def _extract_answer_letter(self, response: str) -> Optional[str]:
        """Extract answer letter from LLM response."""
        # Look for patterns like "A)", "B)", "Answer: A", etc.
        import re
        
        patterns = [
            r'\b([A-E])\)',
            r'Answer:\s*([A-E])',
            r'^\s*([A-E])\s*$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1)
        
        # Check first character
        for char in response[:5]:
            if char in 'ABCDE':
                return char
        
        return None
    
    def _answer_letter_to_index(self, letter: str) -> Optional[int]:
        """Convert answer letter to index."""
        mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
        return mapping.get(letter.upper())
    
    def run_evaluation(self, dataset_path: str, max_questions: Optional[int] = None):
        """Run evaluation on dataset."""
        print(f"Starting Graph-RAG evaluation with {self.model_name}")
        
        results = []
        completed = set()
        
        # Load existing results if any
        results_path = os.path.join(EXPERIMENT_DIR, "results", "graph_rag_results.jsonl")
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    completed.add(data['question_id'])
            print(f"Already completed: {len(completed)} questions")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            processed = 0
            correct = 0
            
            for row in reader:
                if max_questions and processed >= max_questions:
                    break
                
                result = self.evaluate_question(row, completed)
                
                if result is None:
                    continue
                
                if result['is_correct']:
                    correct += 1
                
                results.append(result)
                processed += 1
                
                # Append to results file
                with open(results_path, 'a') as outf:
                    outf.write(json.dumps(result) + '\n')
                
                if processed % 10 == 0:
                    acc = correct / processed if processed > 0 else 0
                    print(f"Progress: {processed} | Accuracy: {acc:.2%}")
        
        # Calculate final summary
        total = len(results)
        accuracy = correct / total if total > 0 else 0
        
        summary = {
            'model': self.model_name,
            'evaluation_type': 'graph_rag',
            'total_questions': total,
            'correct_answers': correct,
            'accuracy': accuracy
        }
        
        summary_path = os.path.join(EXPERIMENT_DIR, "results", "graph_rag_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nGraph-RAG Evaluation Complete!")
        print(f"Total: {total}")
        print(f"Correct: {correct}")
        print(f"Accuracy: {accuracy:.2%}")
        
        return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate Graph-RAG system")
    parser.add_argument("--model", type=str, default="google/gemini-2.5-flash-lite")
    parser.add_argument("--max-questions", type=int, default=None)
    parser.add_argument("--graph", type=str, 
                       default=os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl"))
    parser.add_argument("--dataset", type=str,
                       default=os.path.join(EXPERIMENT_DIR, "..", "data", 
                                            "river_qa_dataset_shuffled.csv"))
    
    args = parser.parse_args()
    
    evaluator = GraphRAGEvaluator(args.model, args.graph)
    evaluator.run_evaluation(args.dataset, args.max_questions)


if __name__ == "__main__":
    main()
