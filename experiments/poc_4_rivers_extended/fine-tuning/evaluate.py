#!/usr/bin/env python3
"""
LLM Evaluation Script for River Q&A Dataset
Evaluates different LLMs (OpenRouter API or local LoRA models) on multiple choice questions.
Supports resumability and saves results incrementally.
"""

import csv
import json
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class LLMEvaluator:
    def __init__(self, model_name, dataset_path, results_dir, local_model_path=None, base_model=None):
        self.model_name = model_name
        self.dataset_path = dataset_path
        self.results_dir = results_dir
        self.local_model_path = local_model_path
        self.base_model = base_model
        
        # Determine if using local or API model
        self.is_local = local_model_path is not None
        
        if not self.is_local:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable not set.")
        else:
            self._load_local_model()
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Sanitize model name for file paths
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        
        # Results file paths
        self.results_file = os.path.join(results_dir, f"{safe_model_name}_results.jsonl")
        self.summary_file = os.path.join(results_dir, f"{safe_model_name}_summary.json")
    
    def _load_local_model(self):
        """Load local LoRA model using unsloth."""
        from unsloth import FastLanguageModel
        import torch
        
        print(f"Loading local model from {self.local_model_path}")
        print(f"Base model: {self.base_model}")
        
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.local_model_path,
            max_seq_length=2048,
            dtype=None,  # Auto-detect
            load_in_4bit=False,  # Set to True if you need 4-bit for memory
        )
        
        # Enable inference mode for speed
        FastLanguageModel.for_inference(self.model)
        
        print("Local model loaded successfully")
    
    def get_llm_response(self, question, answers):
        """Get single character response from LLM (A, B, C, D, or E)."""
        prompt = f"""This is a multiple choice question about US rivers and waterways. Please answer based on your knowledge of American geography and hydrology.

Question: {question}

Answer choices:
A) {answers[0]}
B) {answers[1]}
C) {answers[2]}
D) {answers[3]}
E) {answers[4]}

Respond with only the letter of the correct answer (A, B, C, D, or E)."""

        if self.is_local:
            return self._get_local_response(prompt)
        else:
            return self._get_api_response(prompt)
    
    def _get_local_response(self, prompt):
        """Get response from local LoRA model."""
        try:
            # Format as chat message
            messages = [{"role": "user", "content": prompt}]
            
            # Apply chat template
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize
            inputs = self.tokenizer([formatted_prompt], return_tensors="pt").to(self.model.device)
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=10,
                temperature=0.0,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode only the new tokens
            generated_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            content = generated_text.strip().upper()
            
            # Extract single letter response
            for letter in ['A', 'B', 'C', 'D', 'E']:
                if letter in content:
                    return letter
            
            print(f"Invalid response: {content}")
            return None
            
        except Exception as e:
            print(f"Local model error: {e}")
            return None
    
    def _get_api_response(self, prompt):
        """Get response from OpenRouter API."""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=json.dumps({
                    "model": self.model_name,
                    "temperature": 0.0,
                    "messages": [{"role": "user", "content": prompt}]
                }),
                timeout=10
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].strip().upper()
            
            # Extract single letter response
            for letter in ['A', 'B', 'C', 'D', 'E']:
                if letter in content:
                    return letter
            
            print(f"Invalid response: {content}")
            return None
            
        except Exception as e:
            print(f"API error: {e}")
            return None
    
    def get_completed_questions(self):
        """Get set of already completed question IDs."""
        completed = set()
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        completed.add(data['question_id'])
        return completed
    
    def save_result(self, question_id, question, answers, correct_index, llm_response, is_correct):
        """Save individual result to JSONL file."""
        result = {
            'question_id': question_id,
            'question': question,
            'answers': answers,
            'correct_answer_index': correct_index,
            'correct_answer': answers[correct_index],
            'llm_response': llm_response,
            'is_correct': is_correct,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(result) + '\n')
    
    def evaluate_dataset(self, max_questions=None):
        """Evaluate the dataset, resuming from where it left off."""
        completed = self.get_completed_questions()
        processed = 0
        correct = 0
        
        print(f"Starting evaluation with {self.model_name}")
        print(f"Mode: {'Local' if self.is_local else 'API'}")
        print(f"Already completed: {len(completed)} questions")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
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
                
                print(f"Processing {question_id}.... correct_index: {correct_index}")
                
                llm_response = self.get_llm_response(question, answers)
                
                # Small delay only for API calls
                if not self.is_local:
                    time.sleep(0.05)
                
                if llm_response:
                    # Convert LLM response to index (A=0, B=1, etc.)
                    response_index = ord(llm_response) - ord('A')
                    print(f"LLM response: {llm_response}, response index: {response_index}")
                    is_correct = response_index == correct_index
                    
                    if is_correct:
                        correct += 1
                    
                    self.save_result(question_id, question, answers, correct_index, llm_response, is_correct)
                    processed += 1
                    
                    print(f"  Response: {llm_response}, Correct: {is_correct}")
                else:
                    print(f"  Failed to get valid response")
        
        # Save summary
        self.save_summary(processed, correct)
        return processed, correct
    
    def save_summary(self, total_processed, total_correct):
        """Save evaluation summary."""
        accuracy = total_correct / total_processed if total_processed > 0 else 0
        
        summary = {
            'model': self.model_name,
            'mode': 'local' if self.is_local else 'api',
            'total_questions': total_processed,
            'correct_answers': total_correct,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nEvaluation Summary:")
        print(f"Model: {self.model_name}")
        print(f"Total Questions: {total_processed}")
        print(f"Correct Answers: {total_correct}")
        print(f"Accuracy: {accuracy:.2%}")


def main():
    # Configuration
    dataset_path = 'river_qa_dataset_shuffled.csv'
    results_dir = 'evaluation'
    
    # ===== CHOOSE ONE: API or Local =====
    
    # For OpenRouter API:
    # model_name = "anthropic/claude-sonnet-4.5"
    # evaluator = LLMEvaluator(model_name, dataset_path, results_dir)
    
    # For Local LoRA model:
    model_name = "gemma-3-4b-abstain"  # Name for results files
    local_model_path = "/teamspace/studios/this_studio/gemma-3-4b-abstain-lora"  # Path to LoRA adapter
    base_model = "unsloth/gemma-3-4b-it-unsloth-bnb-4bit"  # Base model used for training
    
    evaluator = LLMEvaluator(
        model_name=model_name,
        dataset_path=dataset_path,
        results_dir=results_dir,
        local_model_path=local_model_path,
        base_model=base_model
    )
    
    # Run evaluation
    evaluator.evaluate_dataset(max_questions=20_000)


if __name__ == "__main__":
    main()