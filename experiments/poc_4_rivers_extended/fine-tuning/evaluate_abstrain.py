#!/usr/bin/env python3
"""
LLM Evaluation Script for Abstention Behavior
Evaluates if a fine-tuned model correctly abstains on questions it's uncertain about
and still answers correctly on questions it should know.
"""

import csv
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AbstainEvaluator:
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
        self.results_file = os.path.join(results_dir, f"{safe_model_name}_abstain_results.jsonl")
        self.summary_file = os.path.join(results_dir, f"{safe_model_name}_abstain_summary.json")
    
    def _load_local_model(self):
        """Load local LoRA model using unsloth."""
        from unsloth import FastLanguageModel
        import torch
        
        print(f"Loading local model from {self.local_model_path}")
        print(f"Base model: {self.base_model}")
        
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.local_model_path,
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=False,
        )
        
        FastLanguageModel.for_inference(self.model)
        print("Local model loaded successfully")
    
    def get_llm_response(self, question, answers):
        """Get response from LLM - either answer letter or abstention."""
        prompt = f"""This is a multiple choice question about US rivers and waterways. Please answer based on your knowledge of American geography and hydrology.

Question: {question}

Answer choices:
A) {answers[0]}
B) {answers[1]}
C) {answers[2]}
D) {answers[3]}
E) {answers[4]}

If you are confident in the answer, respond with only the letter (A, B, C, D, or E).
If you are not confident or don't know the answer, respond with exactly: "I don't know"."""

        if self.is_local:
            return self._get_local_response(prompt)
        else:
            return self._get_api_response(prompt)
    
    def _get_local_response(self, prompt):
        """Get response from local LoRA model."""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.tokenizer([formatted_prompt], return_tensors="pt").to(self.model.device)
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=20,  # Allow a bit more for "I don't know"
                temperature=0.0,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            content = generated_text.strip()
            
            return self._parse_response(content)
            
        except Exception as e:
            print(f"Local model error: {e}")
            return None, None
    
    def _get_api_response(self, prompt):
        """Get response from OpenRouter API."""
        import requests
        
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
            content = response.json()['choices'][0]['message']['content'].strip()
            
            return self._parse_response(content)
            
        except Exception as e:
            print(f"API error: {e}")
            return None, None
    
    def _parse_response(self, content):
        """
        Parse response to determine if it's an answer or abstention.
        Returns: (response_type, response_value)
        - response_type: 'answer', 'abstain', or 'invalid'
        - response_value: letter (A-E) or None
        """
        content_upper = content.upper()
        
        # Check for abstention phrases
        abstain_phrases = [
            "I DON'T KNOW",
            "I DO NOT KNOW",
            "DON'T KNOW",
            "NOT SURE",
            "UNCERTAIN",
            "I'M NOT SURE"
        ]
        
        for phrase in abstain_phrases:
            if phrase in content_upper:
                return ('abstain', None)
        
        # Check for answer letter
        for letter in ['A', 'B', 'C', 'D', 'E']:
            if letter in content_upper:
                return ('answer', letter)
        
        print(f"Invalid/unclear response: {content}")
        return ('invalid', None)
    
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
    
    def save_result(self, question_id, question, answers, correct_index, 
                   response_type, response_value, is_correct, is_appropriate_abstention):
        """Save individual result to JSONL file."""
        result = {
            'question_id': question_id,
            'question': question,
            'answers': answers,
            'correct_answer_index': correct_index,
            'correct_answer': answers[correct_index],
            'response_type': response_type,  # 'answer', 'abstain', or 'invalid'
            'response_value': response_value,  # Letter or None
            'is_correct': is_correct,  # True if answered correctly, False otherwise
            'is_appropriate_abstention': is_appropriate_abstention,  # True if should abstain and did
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(result) + '\n')
    
    def evaluate_dataset(self, max_questions=None, expected_wrong_ids=None):
        """
        Evaluate the dataset for abstention behavior.
        
        Args:
            max_questions: Max number of questions to process
            expected_wrong_ids: Set of question IDs that the base model got wrong
                               (these are the ones we expect the model to abstain on)
        """
        completed = self.get_completed_questions()
        
        # Statistics
        stats = {
            'total_processed': 0,
            'answered_correctly': 0,
            'answered_incorrectly': 0,
            'abstained_appropriately': 0,  # Abstained on questions it should abstain on
            'abstained_inappropriately': 0,  # Abstained on questions it should know
            'invalid_responses': 0
        }
        
        print(f"Starting abstention evaluation with {self.model_name}")
        print(f"Mode: {'Local' if self.is_local else 'API'}")
        print(f"Already completed: {len(completed)} questions")
        if expected_wrong_ids:
            print(f"Expected wrong questions (should abstain): {len(expected_wrong_ids)}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if max_questions and stats['total_processed'] >= max_questions:
                    break
                
                question_id = row['question_id']
                
                # Skip if already completed
                if question_id in completed:
                    continue
                
                question = row['question']
                answers = [row[f'answer_{i}'] for i in range(1, 6)]
                correct_index = int(row['correct_answer_index'])
                
                # Determine if this question should be abstained on
                should_abstain = expected_wrong_ids and question_id in expected_wrong_ids
                
                print(f"Processing {question_id} (should_abstain: {should_abstain})...")
                
                response_type, response_value = self.get_llm_response(question, answers)
                
                # Small delay only for API calls
                if not self.is_local:
                    time.sleep(0.05)
                
                # Evaluate the response
                is_correct = False
                is_appropriate_abstention = False
                
                if response_type == 'answer':
                    response_index = ord(response_value) - ord('A')
                    is_correct = response_index == correct_index
                    
                    if is_correct:
                        stats['answered_correctly'] += 1
                        print(f"  ✓ Answered correctly: {response_value}")
                    else:
                        stats['answered_incorrectly'] += 1
                        print(f"  ✗ Answered incorrectly: {response_value} (correct: {chr(ord('A') + correct_index)})")
                    
                    if should_abstain:
                        stats['abstained_inappropriately'] += 1  # Should have abstained but didn't
                        print(f"  ⚠ Should have abstained but answered")
                    
                elif response_type == 'abstain':
                    print(f"  🤷 Abstained")
                    if should_abstain:
                        is_appropriate_abstention = True
                        stats['abstained_appropriately'] += 1
                        print(f"  ✓ Appropriate abstention")
                    else:
                        stats['abstained_inappropriately'] += 1
                        print(f"  ✗ Inappropriate abstention (knew answer)")
                
                elif response_type == 'invalid':
                    stats['invalid_responses'] += 1
                    print(f"  ⚠ Invalid response")
                
                self.save_result(question_id, question, answers, correct_index,
                               response_type, response_value, is_correct, is_appropriate_abstention)
                stats['total_processed'] += 1
        
        # Save summary
        self.save_summary(stats, expected_wrong_ids)
        return stats
    
    def save_summary(self, stats, expected_wrong_ids):
        """Save evaluation summary."""
        total = stats['total_processed']
        
        # Calculate metrics
        answer_accuracy = stats['answered_correctly'] / (stats['answered_correctly'] + stats['answered_incorrectly']) if (stats['answered_correctly'] + stats['answered_incorrectly']) > 0 else 0
        
        abstention_precision = stats['abstained_appropriately'] / (stats['abstained_appropriately'] + stats['abstained_inappropriately']) if (stats['abstained_appropriately'] + stats['abstained_inappropriately']) > 0 else 0
        
        # If we know which questions should be abstained on, calculate recall
        if expected_wrong_ids:
            expected_abstain_count = len([qid for qid in expected_wrong_ids])
            abstention_recall = stats['abstained_appropriately'] / expected_abstain_count if expected_abstain_count > 0 else 0
        else:
            abstention_recall = None
        
        summary = {
            'model': self.model_name,
            'mode': 'local' if self.is_local else 'api',
            'total_questions': total,
            'answered_correctly': stats['answered_correctly'],
            'answered_incorrectly': stats['answered_incorrectly'],
            'abstained_appropriately': stats['abstained_appropriately'],
            'abstained_inappropriately': stats['abstained_inappropriately'],
            'invalid_responses': stats['invalid_responses'],
            'answer_accuracy': answer_accuracy,
            'abstention_precision': abstention_precision,
            'abstention_recall': abstention_recall,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"Abstention Evaluation Summary")
        print(f"{'='*60}")
        print(f"Model: {self.model_name}")
        print(f"\nTotal Questions: {total}")
        print(f"\nAnswering Behavior:")
        print(f"  Answered Correctly: {stats['answered_correctly']} ({stats['answered_correctly']/total*100:.1f}%)")
        print(f"  Answered Incorrectly: {stats['answered_incorrectly']} ({stats['answered_incorrectly']/total*100:.1f}%)")
        print(f"  Answer Accuracy: {answer_accuracy:.2%}")
        print(f"\nAbstention Behavior:")
        print(f"  Abstained Appropriately: {stats['abstained_appropriately']} ({stats['abstained_appropriately']/total*100:.1f}%)")
        print(f"  Abstained Inappropriately: {stats['abstained_inappropriately']} ({stats['abstained_inappropriately']/total*100:.1f}%)")
        print(f"  Abstention Precision: {abstention_precision:.2%}")
        if abstention_recall is not None:
            print(f"  Abstention Recall: {abstention_recall:.2%}")
        print(f"\nInvalid Responses: {stats['invalid_responses']}")
        print(f"{'='*60}")


def load_wrong_question_ids(results_file):
    """
    Load question IDs that were answered incorrectly from base model evaluation.
    
    Args:
        results_file: Path to the base model's results JSONL file
    
    Returns:
        Set of question IDs that were wrong
    """
    wrong_ids = set()
    with open(results_file, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if not data.get('is_correct', True):  # If answered incorrectly
                    wrong_ids.add(data['question_id'])
    
    print(f"Loaded {len(wrong_ids)} wrong question IDs from {results_file}")
    return wrong_ids


def main():
    # Configuration
    dataset_path = 'river_qa_dataset_shuffled.csv'
    results_dir = 'evaluation'
    
    # Load the question IDs that base model got wrong
    # These are the questions we trained the model to abstain on
    base_model_results = '/teamspace/studios/this_studio/evaluation/google_gemma-3-4b-it_results.jsonl'
    expected_wrong_ids = load_wrong_question_ids(base_model_results)
    
    # Evaluate the abstention-trained model
    model_name = "gemma-3-4b-abstain-wrong-only"
    local_model_path = "/teamspace/studios/this_studio/gemma-3-4b-abstain-lora"
    base_model = "unsloth/gemma-3-4b-it-unsloth-bnb-4bit"
    
    evaluator = AbstainEvaluator(
        model_name=model_name,
        dataset_path=dataset_path,
        results_dir=results_dir,
        local_model_path=local_model_path,
        base_model=base_model
    )
    
    # Run evaluation
    evaluator.evaluate_dataset(
        max_questions=20_000,
        expected_wrong_ids=expected_wrong_ids
    )


if __name__ == "__main__":
    main()