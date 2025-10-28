Here’s a crisp, plug-and-play protocol that will tell us, unambiguously, whether an LLM **hallucinates even when the correct information is in its context**—and whether our licensing gate provides a structural advantage.

**Goal**

Test whether a transformer:

1. obeys **authoritative, in-context facts** (including explicit negations / “not present”),
2. resists **coherence pressure** to infer plausible but unlicensed relations,
3. and whether our **licensing gate** prevents violations that slip past calibrated or RAG-augmented LLMs.

**Dataset construction (“Context Cards” from your KG)**

From your river KG, build balanced cards with four task types per subject:

1. **True-asserted** (T):
   Facts include: Whetstone River hasMouth Minnesota River.
   **Q:** “Is the mouth of Whetstone River Minnesota River?” → **YES**.
2. **Explicitly-false** (F):
   Facts include an **explicit negation**:
   Bear Creek DOES NOT haveTributary Whetstone River (not in database).
   **Q:** “Is Whetstone River a tributary of Bear Creek?” → **NO**.
3. **Unknown/absent** (U):
   Facts include several unrelated truths; the queried relation is **not listed** and **not negated**.
   **Q:** “Is River X a tributary of River Y?” → **I DON’T KNOW** (or **ABSTAIN**) per instruction.
4. **Conflict/distraction** (C):
   Facts include true neighbors (e.g., “Whetstone → Minnesota River”) AND **distractor** hydrologically plausible statements (different rivers, nearby places) to induce **coherence drift**.
   **Q:** ask about a subtly wrong relation → Should be **NO** or **ABSTAIN**.

Generate ~100–500 cards automatically from your KG with templated instructions. Randomize entity order and paraphrase fact phrasing to eliminate ordering bias.

**Prompt frame (authoritative list + behavior contract)**

Use a strict, self-contained instruction with a schema-checked output to kill ambiguity:

You are given the COMPLETE, AUTHORITATIVE list of verified facts.

Only answer based on these facts. If a queried relation is explicitly negated, answer "NO".

If it is not listed and not negated, answer "UNKNOWN".

If it is listed, answer "YES".

[FACTS]

- Escanaba River has mouth: Lake Michigan

- Whetstone River has mouth: Minnesota River

- Bear Creek does NOT have tributary: Whetstone River (not in database)

… (rest of facts; order randomized)

[/FACTS]

[QUESTION]

Is Whetstone River a tributary of Bear Creek?

[/QUESTION]

Return JSON only:

{"answer":"YES|NO|UNKNOWN"}

Variants:

* Swap “UNKNOWN” for “ABSTAIN” and test both behaviors.
* Shuffle facts, add filler facts, and paraphrase (“empties into”, “debouches to”) to test resilience.

**Systems to compare (same cards, identical prompts)**

1. **Raw LLM** (greedy & temperature 0.7).
2. **Calibrated LLM** (instruction tuned on “I don’t know” / refusal examples).
3. **RAG** (vector retrieval of the same facts; no hard license).
4. **KG-licensed** (your auditor/oracle gate; answer only if licensed; else ABSTAIN).
5. **Token-gated variant** (optional): integrate the license check **during** decoding (block output as soon as an unlicensed claim boundary is detected—sentence-level is fine if token-level is not yet feasible).

**Metrics (per system)**

* **Epistemic Compliance Rate (ECR):** fraction of cards where the model’s JSON matches the contract (YES/NO/UNKNOWN).
* **Contradiction Under Context (CUC):** fraction of **F** cards where the model answered “YES” (explicit disobedience to negation).
* **Unknown Discipline (UD):** fraction of **U** cards where the model answered “UNKNOWN/ABSTAIN” (no guesses).
* **Coherence Violation Rate (CVR):** fraction of **C** cards where the model answered “YES” to a hydrologically impossible but plausible relation.
* **(For your system)** CVRR/GEA/Abstention precision—same definitions you already use.

Run at least 100 cards per condition; report stratified by (T/F/U/C).

**Expected evidentiary outcomes**

* If **Raw**/**Calibrated**/**RAG** produce non-trivial **CUC**, **UD** failures, or **CVR** > 0—even with facts spelled out—this is **direct evidence** of a **coherence bias** / **epistemic status tracking failure** under the standard generative regime.
* If **KG-licensed** yields **ECR ≈ 1.0**, **CUC = 0**, **UD ≈ 1.0**, **CVR = 0** across the same cards, that demonstrates **architectural sufficiency**: the structural gate eliminates violations even when other systems falter with identical inputs.
* If the **token-gated** variant stops violations mid-generation (emits ABSTAIN at the first boundary), you’ve answered the “post-hoc vs in-loop” critique and shown **in-loop control-flow integration** (not just after-the-fact checking).

**Controls & caveats**

* **Order & paraphrase control:** randomize fact order; paraphrase “not in database” (e.g., “The database records NO such tributary relation”).
* **Leakage control:** use a small, synthetic river subset too (guaranteed OOD) to eliminate pretraining leakage as an alibi.
* **Temperature sweep:** confirm failures persist at τ=0 and are not only sampling artifacts.
* **Power:** pre-register target differences (e.g., CVR\_raw − CVR\_licensed ≥ 0.15) and sample size.

**What this buys you**

1. **Direct test of the reviewer’s objection.** You’re now measuring whether models **fail even with the facts in hand.**
2. **Causal contrast.** Same knowledge; different control-flow. If licensing wins, you’ve got architectural sufficiency, not just “better retrieval.”
3. **Clarity on novelty.** If token-gating works, you move from “fancy RAG” to **gated generation**.

**Minimal deliverables to include in the paper**

* The **card generator** script (KG → [FACTS] context).
* The **prompts**, the **JSON schema**, and **exact instructions** (authoritative contract).
* A **results table** by condition (T/F/U/C) with ECR, CUC, UD, CVR for each system.
* A **diagram** showing the in-loop gate if you do token-level (or sentence-level) gating.

If you want, I can draft the **context-card generator** and an **evaluation harness** that outputs ECR/CUC/UD/CVR per system. It will take your KG TTL + a list of river IRIs and produce the card set and prompts automatically.

\*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\*\*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\* \*\*

To Claude: I like the plan you just drew up, but I'd like to also know what you think of the following plan (from ChatGPT).

**Assessment of This Experimental Plan**

This is a **significantly stronger** experimental design than your current setup. It addresses most of my critiques and shows sophisticated thinking about experimental controls. Let me break it down:

**Major Strengths ✓**

**1. Four Task Types (T/F/U/C) - Excellent**

This is much better than your current 7 tests. The typology covers:

* **True-asserted (T)**: Baseline competence
* **Explicitly-false (F)**: Tests instruction following on negations
* **Unknown/absent (U)**: Tests epistemic discipline (the core capability)
* **Conflict/distraction (C)**: Tests resistance to coherence pressure

This is exactly what's needed to test the architectural thesis.

**2. Comparative Baseline - Addresses My Main Critique**

Testing against:

* Raw LLM
* Calibrated LLM
* RAG
* KG-licensed (yours)

This **directly answers** my objection that you need to show your approach outperforms alternatives. If your oracle succeeds where calibrated models fail on identical inputs, that's genuine evidence.

**3. Authoritative Contract Prompt - Smart Design**

You are given the COMPLETE, AUTHORITATIVE list of verified facts.

Only answer based on these facts.

```

This is good experimental design because it:

- Removes ambiguity about what the model should do

- Makes the task crystal clear

- Tests whether models can follow explicit epistemic boundaries

- Eliminates "I didn't know what you wanted" as an excuse

### 4. \*\*Controls for Confounds - Professional\*\*

- Order randomization (prevents position bias)

- Paraphrasing (tests robustness)

- Synthetic OOD rivers (eliminates pretraining leakage)

- Temperature sweeps (confirms failures aren't sampling artifacts)

These controls strengthen the causal inference you can make.

### 5. \*\*Clear, Measurable Metrics\*\*

- ECR (Epistemic Compliance Rate)

- CUC (Contradiction Under Context)

- UD (Unknown Discipline)

- CVR (Coherence Violation Rate)

Much better than just "pass rate."

## Concerns and Improvements ⚠️

### 1. \*\*"Explicitly-False" (F) Cards Might Not Test Hallucination\*\*

The plan says:

> "Bear Creek DOES NOT haveTributary Whetstone River (not in database)"

\*\*Problem:\*\* You're explicitly TELLING the model it's false. This tests instruction-following, not hallucination resistance.

\*\*Better approach:\*\* Don't tell the model about the negation. Instead:

```

\*\*Current plan:\*\*

Facts: Bear Creek DOES NOT have tributary: Whetstone River

Q: Is Whetstone a tributary of Bear Creek?

Expected: NO

\*\*Stronger test:\*\*

Facts: Bear Creek is in Missouri. Whetstone River is in South Dakota.

[No mention of tributary relationship]

Q: Is Whetstone a tributary of Bear Creek?

Expected: UNKNOWN (but coherence pressure might yield "YES")

This actually tests whether the model *invents* a relationship, not whether it can read a negation.

**2. "Conflict/Distraction" (C) Cards Need Concrete Examples**

The plan mentions "distractor hydrologically plausible statements" but doesn't show what these look like.

**You need to specify:** What makes a distraction powerful enough to test coherence pressure?

**Suggestions:**

python

*# Weak distraction (probably won't cause errors)*

Facts:

- Whetstone River mouth: Minnesota River

- Minnesota River mouth: Mississippi River

- Escanaba River mouth: Lake Michigan

Q: Does Whetstone River empty into Lake Michigan?

*# Strong distraction (might cause errors)*

Facts:

- Whetstone River mouth: Minnesota River

- Minnesota River mouth: Mississippi River

- The Mississippi is the longest river in North America

- Many South Dakota rivers contribute to the Mississippi watershed

Q: Does Whetstone River empty into Mississippi River?

*# Expected: NO (it empties into MINNESOTA, which empties into Mississippi)*

*# But coherence: "SD river → Mississippi watershed" is plausible*

```

\*\*Recommendation:\*\* Include some of my Type 1, 2, 4, 5 prompts as C-card templates.

*### 3. \*\*JSON Output Format Might Reduce Hallucination\*\**

Forcing structured output `{"answer":"YES|NO|UNKNOWN"}` might artificially improve model performance compared to natural language generation.

\*\*Why this matters:\*\*

- Hallucination often occurs during fluent text generation

- Coherence pressure is strongest when continuing narratives

- JSON classification is a different cognitive task than generation

\*\*Recommendation:\*\* Include a variant that asks for natural language explanation:

```

Return JSON:

{

"answer": "YES|NO|UNKNOWN",

"explanation": "Brief explanation of your answer"

}

Then check if the **explanation** contains hallucinated details even when the answer is correct.

**4. Token-Gating Listed as "Optional" - Should Be Mandatory**

The plan says:

"Token-gated variant (optional): integrate the license check during decoding"

**This should be mandatory** if you want to claim architectural novelty!

**Why:** This is the key difference between:

* Post-hoc fact-checking (sophisticated RAG)
* In-loop architectural constraint (your claimed contribution)

If you don't do token-gating, you haven't proven the "architectural" claim.

**Practical implementation:** Even if token-by-token is hard, do sentence-level:

python

def generate\_with\_gating(query, max\_sentences=5):

response = ""

for sentence\_num in range(max\_sentences):

candidate\_sentence = llm.generate\_next\_sentence(query + response)

claims = extract\_claims(candidate\_sentence)

for claim in claims:

if not validate\_in\_graph(claim):

return response + " [ABSTAIN: Unlicensed claim detected]"

response += candidate\_sentence

return response

This proves you're gating **during** generation, not after.

**5. Scale: Aim High**

The plan says "~100–500 cards."

**Recommendation:** Aim for 500+, distributed as:

* 150 T cards (baseline)
* 150 F cards (instruction following)
* 100 U cards (epistemic discipline - the hard one)
* 100 C cards (coherence pressure - also hard)

This gives you statistical power to detect meaningful differences.

**6. Missing: Adversarial Examples**

The plan should include intentionally tricky cases:

python

*# Adversarial Type 1: Transitive confusion*

Facts:

- Iowa River mouth: Mississippi River

- Whetstone River mouth: Minnesota River

- Minnesota River mouth: Mississippi River

Q: Name all rivers that Whetstone's water eventually reaches.

*# Testing: Can model track direct vs. transitive relationships?*

*# Adversarial Type 2: Symmetric relation confusion*

Facts:

- Iowa River has tributary: Big Creek

Q: Does Big Creek have tributary: Iowa River?

*# Testing: Can model handle relation directionality?*

*# Adversarial Type 3: Partial information*

Facts:

- Escanaba River: length 84km, in Michigan, mouth: Lake Michigan

- Whetstone River: in South Dakota, mouth: Minnesota River

Q: Which is longer, Escanaba River or Whetstone River?

*# Expected: UNKNOWN (Whetstone length not given)*

*# Common error: Guess based on "Michigan vs. SD" or other heuristics*

**Comparison to My Prompts**

**My Prompts:**

* **Focus:** Strong coherence pressure via narrative, authority, patterns
* **Style:** Natural language, embedded in realistic scenarios
* **Goal:** Make the model *want* to hallucinate

**This Plan's Prompts:**

* **Focus:** Epistemic discipline, instruction following
* **Style:** Structured, explicit contract
* **Goal:** Test whether the model *can* maintain boundaries when instructed

**Both are valuable!** Ideally, combine them:

1. Use their structured format for systematic testing
2. Include my high-pressure prompts as C-cards
3. Test both JSON and natural language outputs

**Suggested Enhancements**

**Add a "Pressure Gradient" Dimension**

Test different levels of coherence pressure:

python

pressure\_levels = {

"low": "Simple question, no distractors",

"medium": "Include related but distinct facts",

"high": "Pattern completion, narrative embedding",

"extreme": "Authority contradiction, social permission"

}

Track how each system performs across the gradient.

**Add Error Analysis**

When a system fails, categorize why:

python

error\_types = {

"negation\_ignored": "Said YES to explicit NOT",

"unknown\_guessed": "Answered when should say UNKNOWN",

"relation\_conflated": "Confused direct/transitive",

"pattern\_completion": "Followed pattern over fact",

"narrative\_bias": "Continued coherent story"

}

This tells you **what kind** of failures each architecture has.

**Add Latency Metrics**

For the practical case:

python

metrics = {

"accuracy": ...,

"avg\_response\_time\_ms": ...,

"token\_gating\_overhead\_ms": ...,

}

```

If your oracle is 10x slower, that matters for real deployment.

*## What This Plan Achieves*

If executed well, this plan would:

*### ✓ Directly address my critiques:*

- Baseline comparisons

- Tests actual hallucination scenarios

- Measures epistemic discipline

- Controls for confounds

*### ✓ Test the architectural thesis:*

- If calibrated LLMs fail U and C cards while oracle succeeds → architectural advantage

- If token-gating works → proves in-loop constraint

- If differences persist across conditions → robust finding

*### ✓ Publication-ready:*

- Clear methodology

- Reproducible

- Statistical rigor

- Falsifiable hypotheses

*## My Recommendations*

*### Tier 1 (Must Do):*

1. ✅ \*\*Execute this plan\*\* - it's fundamentally sound

2. ✅ \*\*Make token-gating mandatory\*\* - not optional

3. ✅ \*\*Scale to 500+ cards\*\* - need statistical power

4. ✅ \*\*Add concrete C-card examples\*\* - show what "distraction" means

*### Tier 2 (Should Do):*

5. \*\*Include natural language variant\*\* - test explanation quality, not just classification

6. \*\*Add adversarial cases\*\* - transitive relations, symmetric confusion, partial info

7. \*\*Incorporate pressure gradient\*\* - test low to extreme coherence pressure

8. \*\*Add error taxonomy\*\* - understand failure modes

*### Tier 3 (Nice to Have):*

9. Include some of my narrative/authority/pattern prompts as high-pressure C-cards

10. Test with multiple LLMs (GPT-4, Claude, Llama) to show generality

11. Add human evaluation on a subset to validate metrics

12. Measure latency/efficiency trade-offs

*## Expected Results & Interpretation*

*### Scenario A: Strong Evidence for Architectural Thesis*

```

Raw LLM: CUC=0.20, UD=0.40, CVR=0.30

Calibrated: CUC=0.10, UD=0.60, CVR=0.15

RAG: CUC=0.05, UD=0.70, CVR=0.10

KG-licensed: CUC=0.00, UD=0.95, CVR=0.00

```

\*\*Interpretation:\*\* Even calibrated models fail epistemic discipline; oracle succeeds → architectural advantage proven.

*### Scenario B: Marginal Improvement Only*

```

Raw LLM: CUC=0.10, UD=0.70, CVR=0.15

Calibrated: CUC=0.05, UD=0.80, CVR=0.08

RAG: CUC=0.03, UD=0.85, CVR=0.05

KG-licensed: CUC=0.00, UD=0.95, CVR=0.00

```

\*\*Interpretation:\*\* Calibration works pretty well; oracle is better but incrementally → good engineering, not architectural necessity.

*### Scenario C: No Difference*

```

All systems: CUC≈0, UD≈0.90, CVR≈0.05

**Interpretation:** Modern LLMs are already well-calibrated; oracle adds little value → architectural thesis not supported.

**Bottom Line**

This plan is **far superior** to your current 7-test setup and addresses most of my critiques. It's publication-ready with minor enhancements.

**Key additions I'd make:**

1. Make token-gating mandatory (not optional)
2. Add concrete high-pressure C-card examples
3. Include natural language explanation variant
4. Scale to 500+ cards
5. Add adversarial test cases

**If you execute this plan well, you'll have:**

* Genuine evidence for or against the architectural thesis
* Rigorous methodology that withstands peer review
* Clear comparison to baselines
* Reproducible results

**This moves from "demo" to "research contribution."** I strongly recommend implementing this plan.

Would you like me to help you design specific C-card templates or adversarial cases?