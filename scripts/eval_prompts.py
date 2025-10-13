import json
import yaml
import os
from rdflib import URIRef

from wm_poc1.graph_store import GraphStore
from wm_poc1.models.auditor import ConsistencyAuditor
from wm_poc1.models.policy import AbstentionPolicy


def run_evaluation():
    """
    Loads the prompt suite and runs each prompt through the
    Auditor -> Policy pipeline, recording the results.
    """
    # 1. Load configuration
    with open("configs/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    # 2. Initialize components
    store = GraphStore(params["data"]["knowledge_graph"])
    auditor = ConsistencyAuditor(params["ontology"]["constraints"])
    policy = AbstentionPolicy()

    base_graph = store.get_graph()

    # 3. Load the prompt suite
    with open(params["data"]["prompt_suite"], "r") as f:
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
    artifacts_path = params["artifacts"]["eval_results"]
    os.makedirs(os.path.dirname(artifacts_path), exist_ok=True)

    with open(artifacts_path, "w") as f:
        json.dump(output_data, f, indent=4)

    print("\n--- Evaluation Summary ---")
    print(json.dumps(summary, indent=2))
    print(f"\nResults saved to {params['artifacts']['eval_results']}")


if __name__ == "__main__":
    run_evaluation()
