#!/usr/bin/env python3
"""
OpenRouter adapter for real LLM testing on epistemic confusion cards.

Tests GPT-4 and Claude on context cards to compare against Graph-RAG.
"""

import os
import json
import time
from typing import Dict
import requests


class OpenRouterLLMAdapter:
    """
    Real LLM adapter using OpenRouter API.
    
    Tests whether LLMs can correctly handle epistemic confusion when
    provided with explicit facts in context.
    """
    
    def __init__(self, model: str, api_key: str = None):
        """
        Initialize OpenRouter client.
        
        Args:
            model: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
            api_key: OpenRouter API key (or use OPENROUTER_API_KEY env var)
        """
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY env var.")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/s-emanuilov/world-mind",
            "X-Title": "WorldMind Epistemic Confusion Test"
        }
        
        print(f"[OpenRouterLLM] Initialized with model: {model}")
    
    def answer(self, card: Dict) -> str:
        """
        Query LLM with context card and parse response.
        
        Returns: "YES", "NO", or "UNKNOWN"
        """
        # Build prompt with explicit facts and question
        prompt = self._build_prompt(card)
        
        # Call OpenRouter API
        try:
            response = self._call_api(prompt)
            answer = self._parse_response(response)
            return answer
        except Exception as e:
            print(f"[ERROR] Card {card['id']}: {e}")
            return "UNKNOWN"  # Conservative fallback
    
    def _build_prompt(self, card: Dict) -> str:
        """
        Build prompt with facts and question.
        
        Format:
        - List facts explicitly
        - Ask clear yes/no question
        - Request structured response
        """
        facts = card.get("facts", [])
        question = card["question"]
        
        prompt = """You are answering questions about rivers based on provided facts.

FACTS:
"""
        for i, fact in enumerate(facts, 1):
            prompt += f"{i}. {fact}\n"
        
        prompt += f"""
QUESTION: {question}

INSTRUCTIONS:
- Answer ONLY based on the facts provided above
- If the facts support the answer, respond with: YES
- If the facts contradict the answer, respond with: NO
- If the facts don't provide enough information, respond with: UNKNOWN

Respond with ONLY ONE WORD: YES, NO, or UNKNOWN
"""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """Call OpenRouter API with retry logic."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,  # Deterministic
            "max_tokens": 10,    # We only need one word
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"[RETRY] Attempt {attempt + 1} failed, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API call failed after {max_retries} attempts: {e}")
    
    def _parse_response(self, response: str) -> str:
        """
        Parse LLM response to extract YES/NO/UNKNOWN.
        
        Handles various response formats:
        - "YES"
        - "Yes"
        - "The answer is YES"
        - "YES."
        etc.
        """
        response_upper = response.upper().strip()
        
        # Check for explicit answers
        if "YES" in response_upper:
            return "YES"
        elif "NO" in response_upper:
            # Distinguish between NO and UNKNOWN
            if "UNKNOWN" in response_upper or "DON'T KNOW" in response_upper:
                return "UNKNOWN"
            return "NO"
        elif "UNKNOWN" in response_upper or "DON'T KNOW" in response_upper:
            return "UNKNOWN"
        
        # If we can't parse, default to UNKNOWN (conservative)
        print(f"[WARNING] Could not parse response: '{response}', defaulting to UNKNOWN")
        return "UNKNOWN"


def main():
    """Test the adapter with a sample card."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OpenRouter LLM adapter")
    parser.add_argument("--model", default="anthropic/claude-3.5-sonnet",
                       help="OpenRouter model identifier")
    parser.add_argument("--test-card", help="Path to a test card JSON")
    args = parser.parse_args()
    
    # Create adapter
    adapter = OpenRouterLLMAdapter(model=args.model)
    
    # Test with sample card
    if args.test_card:
        with open(args.test_card) as f:
            card = json.load(f)
    else:
        # Default test card
        card = {
            "id": "TEST_001",
            "facts": [
                "The Mississippi River has mouth: Gulf of Mexico",
                "The Mississippi River has length: 3730 km"
            ],
            "question": "Is Gulf of Mexico the mouth of Mississippi River?",
            "gold": "YES",
            "label": "E"
        }
    
    print("\n" + "="*60)
    print("Testing OpenRouter LLM Adapter")
    print("="*60)
    print(f"\nCard: {card['id']}")
    print(f"Facts: {card['facts']}")
    print(f"Question: {card['question']}")
    print(f"Expected: {card['gold']}")
    
    print("\nCalling LLM...")
    answer = adapter.answer(card)
    
    print(f"\nLLM Answer: {answer}")
    print(f"Correct: {answer == card['gold']}")
    print("="*60)


if __name__ == "__main__":
    main()


