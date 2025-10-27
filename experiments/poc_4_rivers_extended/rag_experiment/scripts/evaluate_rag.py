#!/usr/bin/env python3
"""
RAG Evaluation System
Evaluates RAG performance on the rivers Q&A dataset and compares with direct LLM evaluation.
"""

import csv
import json
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
import sys

# Add parent directory to path to import retrieval system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from retrieval_system import RetrievalSystem

load_dotenv()

class RAGEvaluator:
    def __init__(self, config_path: str, model_name: str):
        """Initialize RAG evaluator."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.model_name = model_name
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set.")
        
        # Initialize retrieval system
        self.retrieval = RetrievalSystem(config_path)
        
        # Results file paths
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        self.results_file = f"results/rag_{safe_model_name}_results.jsonl"
        self.summary_file = f"results/rag_{safe_model_name}_summary.json"
        
        # Create results directory
        os.makedirs("results", exist_ok=True)
    
    def get_llm_response_with_context(self, question: str, answers: List[str], context: str) -> str:
        """Get LLM response with RAG context."""
        prompt = f"""This is a multiple choice question about US rivers and waterways. Use the provided context to answer the question accurately.

Context:
{context}

Question: {question}

Answer choices:
A) {answers[0]}
B) {answers[1]}
C) {answers[2]}
D) {answers[3]}
E) {answers[4]}

Based on the context provided, respond with only the letter of the correct answer (A, B, C, D, or E)."""

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=json.dumps({
                    "model": self.model_name,
                    "temperature": 0.0,
                    "messages": [{"role": "user", "content": prompt}]
                }),
                timeout=15
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].strip().upper()
            
            # Extract single letter response
            for letter in ['A', 'B', 'C', 'D', 'E']:
                if letter in content:
                    return letter
            
            print(f"Invalid response: {content}")
            return None  # Invalid response
            
        except Exception as e:
            print(f"API error: {e}")
            return None
    
    def get_completed_questions(self) -> set:
        """Get set of already completed question IDs."""
        completed = set()
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        completed.add(data['question_id'])
        return completed
    
    def save_result(self, question_id: str, question: str, answers: List[str], 
                   correct_index: int, llm_response: str, is_correct: bool,
                   context: str, retrieval_info: Dict[str, Any]):
        """Save individual result to JSONL file."""
        result = {
            'question_id': question_id,
            'question': question,
            'answers': answers,
            'correct_answer_index': correct_index,
            'correct_answer': answers[correct_index],
            'llm_response': llm_response,
            'is_correct': is_correct,
            'context': context,
            'retrieval_info': retrieval_info,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(result) + '\n')
    
    def get_current_accuracy(self) -> tuple:
        """Get current accuracy from existing results."""
        completed = self.get_completed_questions()
        if not completed:
            return 0, 0, 0.0
        
        correct_count = 0
        total_count = len(completed)
        
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data['is_correct']:
                            correct_count += 1
        
        accuracy = correct_count / total_count if total_count > 0 else 0.0
        return correct_count, total_count, accuracy

    def show_status(self):
        """Show current evaluation status without running evaluation."""
        completed = self.get_completed_questions()
        correct_count, total_count, accuracy = self.get_current_accuracy()
        
        print(f"RAG Evaluation Status for {self.model_name}")
        print(f"{'='*50}")
        print(f"Completed questions: {len(completed)}")
        print(f"Correct answers: {correct_count}")
        print(f"Total questions: {total_count}")
        print(f"Current accuracy: {accuracy:.2%}")
        print(f"Results file: {self.results_file}")
        print(f"{'='*50}")
        
        return correct_count, total_count, accuracy

    def evaluate_dataset(self, max_questions: int = None):
        """Evaluate the dataset with RAG, resuming from where it left off."""
        completed = self.get_completed_questions()
        processed = 0
        correct = 0
        
        # Get current accuracy from existing results
        existing_correct, existing_total, existing_accuracy = self.get_current_accuracy()
        
        print(f"Starting RAG evaluation with {self.model_name}")
        print(f"Already completed: {len(completed)} questions")
        print(f"Current accuracy: {existing_correct}/{existing_total} = {existing_accuracy:.2%}")
        print(f"{'='*60}")
        
        dataset_path = self.config['data_paths']['questions']
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if max_questions and processed >= max_questions:
                    break
                
                question_id = row['question_id']
                
                # Skip if already completed
                if question_id in completed:
                    continue
                
                question = row['question']
                answers = [row[f'answer_{i}'] for i in range(1, 6)]
                correct_index = int(row['correct_answer_index'])
                river_name = row['river_name']
                
                print(f"Processing {question_id} ({river_name})...")
                
                # Retrieve relevant context
                retrieval_results = self.retrieval.retrieve_for_question(question, river_name)
                context = self.retrieval.get_context_for_question(question, river_name)
                
                # Prepare retrieval info
                retrieval_info = {
                    'num_results': len(retrieval_results),
                    'top_similarity': retrieval_results[0]['similarity_score'] if retrieval_results else 0.0,
                    'river_found': any(river_name.lower() in r['river_name'].lower() for r in retrieval_results),
                    'results': [{'river_name': r['river_name'], 'similarity': r['similarity_score']} for r in retrieval_results[:3]]
                }
                
                # Get LLM response with context
                llm_response = self.get_llm_response_with_context(question, answers, context)
                
                # Small delay to prevent rate limiting
                time.sleep(0.1)
                
                if llm_response:
                    # Convert LLM response to index (A=0, B=1, etc.)
                    response_index = ord(llm_response) - ord('A')
                    is_correct = response_index == correct_index
                    
                    if is_correct:
                        correct += 1
                    
                    self.save_result(question_id, question, answers, correct_index, 
                                   llm_response, is_correct, context, retrieval_info)
                    processed += 1
                    
                    # Calculate running accuracy
                    total_questions = existing_total + processed
                    total_correct = existing_correct + correct
                    current_accuracy = total_correct / total_questions if total_questions > 0 else 0.0
                    
                    print(f"  Response: {llm_response}, Correct: {is_correct}, Similarity: {retrieval_info['top_similarity']:.3f}")
                    print(f"  Running Accuracy: {total_correct}/{total_questions} = {current_accuracy:.2%}")
                    
                    # Show progress every 10 questions
                    if processed % 10 == 0:
                        print(f"  Progress: {processed} new questions processed | Total: {total_questions} | Accuracy: {current_accuracy:.2%}")
                else:
                    print(f"  Failed to get valid response")
        
        # Calculate final totals including existing results
        final_total = existing_total + processed
        final_correct = existing_correct + correct
        final_accuracy = final_correct / final_total if final_total > 0 else 0.0
        
        # Save summary
        self.save_summary(processed, correct)
        
        print(f"\n{'='*60}")
        print(f"EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(f"New questions processed: {processed}")
        print(f"New correct answers: {correct}")
        print(f"Total questions: {final_total}")
        print(f"Total correct answers: {final_correct}")
        print(f"Final accuracy: {final_accuracy:.2%}")
        print(f"{'='*60}")
        
        return processed, correct
    
    def save_summary(self, new_processed: int, new_correct: int):
        """Save evaluation summary."""
        # Get existing totals
        existing_correct, existing_total, _ = self.get_current_accuracy()
        
        # Calculate final totals
        total_processed = existing_total + new_processed
        total_correct = existing_correct + new_correct
        accuracy = total_correct / total_processed if total_processed > 0 else 0
        
        summary = {
            'model': self.model_name,
            'evaluation_type': 'RAG',
            'new_questions': new_processed,
            'new_correct': new_correct,
            'total_questions': total_processed,
            'total_correct': total_correct,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nRAG Evaluation Summary:")
        print(f"Model: {self.model_name}")
        print(f"New Questions: {new_processed}")
        print(f"New Correct: {new_correct}")
        print(f"Total Questions: {total_processed}")
        print(f"Total Correct: {total_correct}")
        print(f"Accuracy: {accuracy:.2%}")


def main():
    """Main evaluation function."""
    import sys
    
    config_path = 'config/rag_config.json'
    model_name = "google/gemini-2.5-flash-lite"  # Same model as direct evaluation
    
    # Create evaluator
    evaluator = RAGEvaluator(config_path, model_name)
    
    # Check if user wants status only
    if len(sys.argv) > 1 and sys.argv[1] == '--status':
        evaluator.show_status()
        return
    
    # Run evaluation
    evaluator.evaluate_dataset(max_questions=20000)  # Start with smaller subset


if __name__ == "__main__":
    main()
