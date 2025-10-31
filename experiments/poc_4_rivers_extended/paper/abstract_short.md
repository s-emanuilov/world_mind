# Abstract (Short Version)

Large language model hallucination persists despite advances in scale and training. We test whether this limitation is architectural rather than statistical by evaluating five approaches on 17,726 question-answer pairs about U.S. rivers: baseline generation, fine-tuning for factual recall and abstention, embedding-based RAG, and graph-based RAG with formal validation. Supervised fine-tuning degraded performance (16.7% → 8.5%) while abstention training achieved only 56.7% precision. Both RAG systems achieved ~89% accuracy through context provision, but only graph-based RAG with a licensing oracle—enforcing mandatory SHACL validation on 118,047 RDF triples—provides deterministic abstention and formal verification alongside high accuracy. These results demonstrate that factual reliability requires architectural enforcement through structural coupling with formal knowledge representations. We introduce the licensing oracle paradigm where knowledge graphs function as active validation gates rather than passive retrieval sources, showing that hallucination mitigation demands architectural innovation rather than statistical optimization.

---

**Keywords**: Large language models, hallucination, knowledge graphs, RAG, SHACL validation, truth-constrained architectures

**Word count**: 170 words

---

## When to Use Which Version

**Long version (291 words)**: Use for journals, conferences, or preprint servers with generous abstract limits (250-300 words). Provides comprehensive coverage of methodology and results.

**Short version (170 words)**: Use for venues with strict limits (150-200 words) or when space is at a premium. Maintains all key findings while reducing methodological detail.





