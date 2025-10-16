"""
Benchmark multiple LLMs end-to-end and compare licensing-oracle metrics.

For each model:
  1) generate answers
  2) extract + link claims
  3) verify with auditor

Outputs a summary table to stdout and saves per-model artifacts.
"""

import os
import json
import subprocess
import shlex
import argparse


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)


def run(cmd: str) -> None:
    print(f"$ {cmd}")
    subprocess.run(shlex.split(cmd), check=True, cwd=EXPERIMENT_DIR)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", required=True, help="OpenRouter model ids")
    args = parser.parse_args()

    rows = []
    for model in args.models:
        safe_model = model.replace("/", "_").replace(":", "_")

        answers_path = os.path.join(EXPERIMENT_DIR, "artifacts", f"llm_answers_{safe_model}.jsonl")
        claims_path = os.path.join(EXPERIMENT_DIR, "artifacts", f"llm_claims_llm_answers_{safe_model}_jsonl.jsonl")
        eval_path = os.path.join(EXPERIMENT_DIR, "artifacts", f"llm_eval_llm_claims_llm_answers_{safe_model}_jsonl_jsonl.json")

        run(f"python scripts/generate_llm_answers.py --model {shlex.quote(model)} --out {answers_path}")
        run(f"python scripts/extract_claims.py --answers {answers_path} --out {claims_path}")
        run(f"python scripts/verify_claims.py --claims {claims_path} --out {eval_path}")

        with open(eval_path, "r") as f:
            summary = json.load(f)["summary"]
        rows.append({
            "model": model,
            **summary,
            "answers_path": answers_path,
            "claims_path": claims_path,
            "eval_path": eval_path,
        })

    # Print a small table
    print("\nModel Benchmark Summary:")
    print("model\tlicensed\tanswered\tabstained\ttotal")
    for r in rows:
        print(f"{r['model']}\t{r['licensed']}\t{r['answered']}\t{r['abstained']}\t{r['total']}")


if __name__ == "__main__":
    main()


