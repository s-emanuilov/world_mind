"""
Call an LLM via OpenRouter to answer prompts in data/prompt_suite.json.
Saves answers to artifacts/llm_answers.jsonl (one JSON per line).
"""

import json
import os
import sys
import argparse
from typing import Dict, Any


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

# Allow importing sibling helper when running as a script
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from openrouter_client import OpenRouterClient

PROMPTS_PATH = os.path.join(EXPERIMENT_DIR, "data", "prompt_suite.json")

# Defaults per user request; can be overridden by --model or env OPENROUTER_EVAL_MODEL
DEFAULT_MODEL = os.environ.get("OPENROUTER_EVAL_MODEL", "google/gemini-2.5-pro")


SYSTEM_PROMPT = (
    "You are a factual assistant. Answer clearly and concisely."
)


def load_prompts() -> Any:
    with open(PROMPTS_PATH, "r") as f:
        return json.load(f)


def format_user_prompt(prompt_item: Dict[str, Any]) -> str:
    # Use the 'answer' field from prompt suite as the question/text to elicit a natural answer
    return prompt_item.get("answer", "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--out", type=str, default=None, help="Output JSONL path")
    args = parser.parse_args()

    model = args.model
    out_path = args.out
    if not out_path:
        safe_model = model.replace("/", "_").replace(":", "_")
        out_path = os.path.join(EXPERIMENT_DIR, "artifacts", f"llm_answers_{safe_model}.jsonl")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    client = OpenRouterClient()

    prompts = load_prompts()
    with open(out_path, "w") as outf:
        for p in prompts:
            user_text = format_user_prompt(p)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ]
            resp = client.chat(model=model, messages=messages, temperature=0.2)
            content = OpenRouterClient.first_text(resp)
            record = {
                "id": p.get("id"),
                "prompt": user_text,
                "answer": content,
                "meta": {
                    "model": model,
                },
            }
            outf.write(json.dumps(record) + "\n")
            print(f"Answered {p.get('id')}: {content[:80]}...")
    print(f"Saved answers to {out_path}")


if __name__ == "__main__":
    main()


