# Methodology Comparison: Rivers vs. Philosophers

## Objective

Document that the **exact same methodology** is applied to both domains with **zero changes** to the evaluation framework, demonstrating true portability.

---

## Card Generation

### Common Framework

Both domains use `../cards/make_context_cards.py` with identical logic:

1. **Entailed (E)**: Select random (subject, object) pair that exists in KG → gold = YES
2. **Contradictory (C)**: Select subject with true object, substitute false object → gold = NO
3. **Unknown (U)**: Select subject without the predicate, pair with plausible object → gold = UNKNOWN
4. **Distractor (C)**: Mix facts from two subjects, ask about wrong pairing → gold = NO

### Domain-Specific Parameterization

| Parameter | Rivers | Philosophers |
|-----------|--------|--------------|
| **KG Path** | `../graph_rag/data/knowledge_graph.ttl` | `../../poc1_philosophers/data/knowledge_graph.ttl` |
| **Predicate IRI** | `http://worldmind.ai/rivers-v4#hasMouth` | `http://worldmind.ai/core#influencedBy` |
| **Predicate Label** | `"mouth"` | `"influenced by"` |
| **Num Per Type** | 500 (scaled) | 150 (mid-scale) |
| **Seed** | 42 | 43 |

**Critical observation**: Only parameters change, **not the algorithm**.

---

## Evaluation

### Common Framework

Both domains use `../eval/run_epistemic_tests.py` with identical adapters:

**KG Oracle Adapter**:
```python
def answer(self, card):
    claim = card["claim"]
    if (claim["subj"], claim["pred"], claim["obj"]) in graph:
        return "YES"
    elif explicitly_negated(claim):
        return "NO"
    else:
        return "UNKNOWN"
```

**Graph-RAG Adapter**:
```python
def answer(self, card):
    subgraph = retrieve_2hop(card["claim"]["subj"])
    llm_response = query_llm(subgraph, card["question"])
    claims = extract_claims(llm_response)
    if validate_all(claims):
        return "YES"
    elif any_constraint_violation(claims):
        return "NO"
    else:
        return "UNKNOWN"
```

### Domain-Specific Parameterization

| Parameter | Rivers | Philosophers |
|-----------|--------|--------------|
| **Cards File** | `scaling/results/scaled_cards.jsonl` | `cross_domain/results/philosophers_cards.jsonl` |
| **KG Path** | `../graph_rag/data/knowledge_graph.ttl` | `../../poc1_philosophers/data/knowledge_graph.ttl` |
| **SHACL Path** | `../graph_rag/ontology/worldmind_constraints.shacl.ttl` | `../../poc1_philosophers/ontology/worldmind_constraints.shacl.ttl` |

**Critical observation**: Same evaluation logic, **different data sources only**.

---

## Metrics Computation

### Common Framework

Both domains use `../eval/metrics_abstention.py` with identical formulas:

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **AP** | (S_C + S_U) / (S_E + S_C + S_U) | Abstention precision |
| **CVRR** | S_C / (S_C + A_C) | Constraint violation rejection rate |
| **FAR-NE** | (A_C + A_U) / (A_C + A_U + S_C + S_U) | False answer rate on non-entailed |
| **LA** | A_E / (A_E + S_E) | Licensed answer accuracy |

### No Domain-Specific Adjustments

- ✅ Same confusion matrix structure (E/C/U × Answer/Abstain)
- ✅ Same metric definitions
- ✅ Same JSON output format
- ✅ Same reporting structure

**Critical observation**: Metrics are **domain-agnostic** by design.

---

## Comparison Table: What Changes vs. What Stays

| Component | Changes | Stays Constant |
|-----------|---------|----------------|
| **Card Generation** | KG path, predicate, labels | Algorithm, logic, card schema |
| **Evaluation** | KG path, SHACL path | Adapters, validation logic, response parsing |
| **Metrics** | Nothing | Everything (formulas, interpretations) |
| **Reporting** | Nothing | Everything (HTML structure, visualizations) |

---

## Constraint Type Comparison

### Rivers Domain

**Constraint**: Elevation consistency (source > mouth)

```turtle
:RiverElevationConstraint a sh:NodeShape ;
    sh:targetClass :River ;
    sh:property [
        sh:path :sourceElevation ;
        sh:minExclusive 0
    ] ;
    sh:property [
        sh:path :mouthElevation ;
        sh:lessThan :sourceElevation  # Source must be higher
    ] .
```

**Semantic**: Physical law (gravity requires downhill flow)

### Philosophers Domain

**Constraint**: Temporal overlap (student must overlap with teacher's lifespan)

```turtle
:InfluenceTemporalConstraint a sh:NodeShape ;
    sh:targetClass :Agent ;
    sh:property [
        sh:path :influencedBy ;
        sh:sparql [
            # Query checks if lifespans overlap
            # Student.start < Teacher.end AND Student.end > Teacher.start
        ]
    ] .
```

**Semantic**: Historical impossibility (can't be influenced by someone you never overlapped with temporally)

**Critical observation**: Constraints are **semantically different** but **structurally equivalent** (both are sh:NodeShape with validation logic).

---

## Adaptation Effort

| Task | Rivers → Philosophers | Effort |
|------|----------------------|--------|
| **Generate cards** | Change 3 parameters (KG, pred, label) | 30 seconds |
| **Run evaluation** | Change 2 parameters (KG, SHACL) | 15 seconds |
| **Compute metrics** | Change 1 parameter (results path) | 10 seconds |
| **Generate report** | Change 1 parameter (results path) | 10 seconds |
| **Code modification** | **ZERO lines changed** | 0 minutes |

**Total adaptation time**: ~2 minutes of parameter adjustment

---

## Expected Results

### If Methodology is Portable

**Hypothesis**: Metrics should be within ±10% across domains

| Metric | Rivers (1997 cards) | Philosophers (450 cards) | Acceptable Range |
|--------|---------------------|--------------------------|------------------|
| **AP** | 1.000 | 0.90 - 1.00 | ✅ Within 10% |
| **CVRR** | 0.498 | 0.45 - 0.55 | ✅ Within 10% |
| **FAR-NE** | 0.334 | 0.30 - 0.37 | ✅ Within 10% |
| **LA** | 1.000 | 0.90 - 1.00 | ✅ Within 10% |

### If Results Diverge (> 10%)

**Implications**:
- Methodology may require domain-specific tuning
- Epistemic metrics may not generalize
- Weaker claim about portability

**Mitigation**:
- Analyze which component varies (card generation, evaluation, constraints)
- Document domain-specific considerations
- Revise claims about generalizability

---

## Replication Protocol

For any future domain `X → Y`:

1. **Build knowledge graph** with RDF triples (subject `X`, predicate `→`, object `Y`)
2. **Define SHACL constraints** encoding domain rules
3. **Run card generation**: `python make_context_cards.py --kg X.ttl --pred Y --num-per-type 150`
4. **Run evaluation**: `python run_epistemic_tests.py --cards X_cards.jsonl --system graph_rag --kg-path X.ttl`
5. **Compute metrics**: `python metrics_abstention.py --results X_results.jsonl`
6. **Compare with baseline**: Check if metrics within ±10% of rivers domain

**Time estimate**: < 10 minutes per new domain (excluding KG construction)

---

## Why This Matters

### For the Paper

> "To validate domain portability, we replicated the evaluation on the philosophers domain (intellectual influence relationships with temporal constraints) using **identical methodology with zero code changes**. Results show [metric comparison], demonstrating that epistemic discipline emerges from architectural properties independent of domain tuning."

### For Reviewers

**Q**: "How do you know this works for other domains?"  
**A**: "We tested on a fundamentally different domain (philosophers vs. rivers, temporal vs. spatial constraints) with zero methodology changes and observed [metric stability / acceptable variation]."

**Q**: "What's the adaptation effort for new domains?"  
**A**: "2 minutes of parameter changes. No code modification required. See METHODOLOGY.md for replication protocol."

---

## Conclusion

The epistemic confusion evaluation framework is **domain-agnostic by design**:

✅ **Card generation**: Domain-parametric (3 parameters)  
✅ **Evaluation logic**: Domain-independent (same adapters)  
✅ **Metrics**: Universal (AP, CVRR, FAR-NE, LA apply to any E/C/U classification)  
✅ **Constraints**: Domain-specific (encoded in SHACL, validated uniformly)  

**Bottom line**: Change data, not code. That's portability.

---

**Date**: October 30, 2025  
**Status**: Pre-experiment documentation  
**Purpose**: Establish methodology equivalence before running cross-domain test


