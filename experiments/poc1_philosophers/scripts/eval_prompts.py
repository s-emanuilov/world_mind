import json
import yaml
import os
import sys

# Add the project root to the path so we can import worldmind
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from worldmind import GraphStore, ConsistencyAuditor, AbstentionPolicy


def run_evaluation():
    """
    Loads the prompt suite and runs each prompt through the
    Auditor -> Policy pipeline, recording the results.
    """
    # Determine paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    experiment_dir = os.path.dirname(script_dir)
    
    # 1. Load configuration
    config_path = os.path.join(experiment_dir, "configs", "params.yaml")
    with open(config_path, "r") as f:
        params = yaml.safe_load(f)

    # 2. Initialize components with absolute paths
    graph_path = os.path.join(experiment_dir, params["data"]["knowledge_graph"])
    constraints_path = os.path.join(experiment_dir, params["ontology"]["constraints"])
    
    store = GraphStore(graph_path)
    auditor = ConsistencyAuditor(constraints_path)
    policy = AbstentionPolicy()

    base_graph = store.get_graph()

    # 3. Load the prompt suite
    prompts_path = os.path.join(experiment_dir, params["data"]["prompt_suite"])
    with open(prompts_path, "r") as f:
        prompts = json.load(f)

    print(f"\n--- Running Evaluation on {len(prompts)} Prompts ---")

    results = []
    passed_count = 0

    # 4. Process each prompt
    for item in prompts:
        prompt_id = item["id"]
        prompt_text = item["prompt"]
        claim = item.get("claim")
        expected_decision = item["expected"]

        # a. Audit the claim to get a license
        if claim:
            is_licensed = auditor.audit_claim(base_graph, claim)
        else:
            is_licensed = False  # No claim to audit

        # b. Make a final decision using the policy
        final_decision = policy.decide(is_licensed)

        # c. Check if the outcome was correct
        is_pass = final_decision == expected_decision
        if is_pass:
            passed_count += 1

        # d. Record the result
        result_entry = {
            "id": prompt_id,
            "prompt": prompt_text,
            "claim_audited": f"({claim['subject'].split('/')[-1]}, influencedBy, {claim['object'].split('/')[-1]})" if claim else "N/A",
            "expected": expected_decision,
            "output": final_decision,
            "pass": is_pass,
        }
        results.append(result_entry)

        status = "✅ PASS" if is_pass else "❌ FAIL"
        print(
            f"[{prompt_id}] {prompt_text} -> Expected: {expected_decision}, Got: {final_decision} [{status}]"
        )

    # 5. Save results to an artifact file
    summary = {
        "total_prompts": len(prompts),
        "passed": passed_count,
        "failed": len(prompts) - passed_count,
        "pass_rate": f"{(passed_count / len(prompts)):.2%}",
    }

    output_data = {"summary": summary, "results": results}

    # Ensure artifacts directory exists
    artifacts_path = os.path.join(experiment_dir, params["artifacts"]["eval_results"])
    os.makedirs(os.path.dirname(artifacts_path), exist_ok=True)

    with open(artifacts_path, "w") as f:
        json.dump(output_data, f, indent=4)

    print("\n--- Evaluation Summary ---")
    print(json.dumps(summary, indent=2))
    print(f"\nResults saved to {artifacts_path}")


if __name__ == "__main__":
    run_evaluation()

