This looks great. A quick read on what you’ve shared:

* Your prompt evaluation shows **7/7 passing** (100% pass rate), with the auditor answering licensed “mouth” relations and abstaining on the fabricated tributary case (TRX1). That aligns perfectly with the licensing/abstention thesis.
* The prompt suite itself is cleanly structured: one invalid tributary claim (TRX1, expected ABSTAIN) and six valid **hasMouth** claims (MTH1–MTH6, expected ANSWER). The subjects/objects are DBpedia IRIs; predicates are in a rivers# namespace—exactly what we want for domain-local relations.

Given your note—**17 rivers, 147 triples, SHACL-validated**, 7 prompts at 100%—I agree this already demonstrates cross-domain portability: you’ve switched from people/time to **hydrology** and got the same behavior (licensed claims pass; unlicensed abstain). That’s the core “ontological repair” result.

Here’s what I’d tighten or add next, to convert this into a robust, publishable result:

**1) Expand the test surface**

* **Balance the suite**: add more *invalid* claims of several kinds, not just one tributary:
  + Wrong mouths (e.g., “Iowa River → Missouri River”),
  + Wrong type targets (river → town),
  + Near-name decoys (“Minnesota River” vs “Minnesota River **(tributary)**”).
* **Noise & aliasing**: repeat the same ground truth with:
  + different capitalization and punctuation,
  + common aliases for rivers, harbors, and bays,
  + spelling variants (US/UK), and parenthetical disambiguations—your suite already includes one such name in MTH4; add more.

**2) Strengthen shapes (domain/range + functionals)**

* Keep **domain/range** constraints in SHACL for river relations (e.g., hasMouth(domain=River, range=WaterBody)); they’ll catch “type-flip” errors quickly.
* Consider **functional-ish** checks where appropriate:
  + A river should not have two distinct mouths (unless explicitly modeled); encode as a warning or violation.
* Optional: add a “**same-as**/alias\*\*” reconciliation step to normalize common IRIs before license checks.

**3) Report the right metrics**

Alongside “prompt pass rate,” add:

* **Coverage–accuracy** (for all audited claims): report accuracy at fixed coverage and show how abstention preserves accuracy.
* **CVRR** (Constraint Violation Rejection Rate): the fraction of constraint-breaking claims that are correctly rejected (abstained).
* **GEA** (Graph Entailment Accuracy): ANSWER only when the triple is present/entailed.
* **Abstention precision** on invalids (you’ll likely be ~1.0 now, but quantify it).
  These will help reviewers see that the performance comes from the **licensing** gate, not just prompt luck.

**4) Add multi-hop and “unknown” cases**

* Multi-hop: a tributary-of-tributary chain (or river→mouth→basin), to show the graph actually enables slightly deeper checks than a flat lookup.
* “Unknown” vs “False”: separate cases where the graph is silent (open-world) from cases that **contradict** SHACL (closed-world on shapes). In both, the system should **ABSTAIN**; label these differently in your suite/results.

**5) Provenance and reasons (optional but nice)**

* When an ANSWER is licensed, echo the **IRI(s)** or mark\_id used (bundle citation).
* When ABSTAIN, log **why** (e.g., “no triple entailed,” “domain/range violation,” “temporal/shape violation”). This doubles as a debugging and explainability layer.

**6) Stress for generalization**

* Copy this exact recipe to **another domain slice** (e.g., **roads → terminus**, **lakes → outflow**, or even **airports → servedCity**). If you get the same 100% behavior on a new micro-KG, you’ve shown the architecture is truly **generic**.

**Specific notes on the attached JSONs**

* The evaluation JSON records **pass = true** for each item, with **expected** and **output** matching (ANSWER for MTH1–MTH6; ABSTAIN for TRX1). That’s the behavior you want to publish as the minimal claim.
* The suite enumerates clear categories (mouth\_valid, tributary\_invalid\_not\_in\_graph) and uses canonical IRIs—good for repeatability and for graph joins later (e.g., to fetch provenance for cites).

**Bottom line**

You’ve just shown the “marks/KG as licensing oracle” **works unchanged** in a non-temporal domain (rivers): **licensed facts → ANSWER; absent/unlicensed → ABSTAIN**—with 100% prompt-level pass on your initial set. Next, grow the negative space, add type/shape violations, and log a couple of multi-hop wins. With those in, you’ll have a compelling cross-domain section for the paper.

If you want, I can:

* auto-generate **near-miss negatives** from your knowledge\_graph.ttl (swap objects to sibling water bodies) and append them to prompt\_suite.json,
* add a small metrics block (CVRR, GEA, abstention precision) to your HTML report,
* wire a “**reasons**” field in the auditor output (e.g., license\_reason="triple\_entailed" or license\_reason="domain\_range\_violation").