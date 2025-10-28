# Abstract

Large language model hallucination persists despite advances in scale and training. We test whether this limitation is architectural rather than statistical by evaluating five approaches on 17,726 question-answer pairs about U.S. rivers: baseline generation, fine-tuning for factual recall and abstention, embedding-based RAG, and graph-based RAG with formal validation. Fine-tuning degraded performance (16.7% → 8.5%) while abstention training achieved only 56.7% precision. Both RAG systems reached ~89% accuracy through context provision, but only graph-based RAG with a licensing oracle—enforcing mandatory SHACL validation on 118,047 RDF triples—provides deterministic abstention and formal verification alongside high accuracy. We introduce the licensing oracle paradigm where knowledge graphs function as active validation gates rather than passive retrieval sources. Results demonstrate that factual reliability requires architectural enforcement through structural coupling with formal knowledge representations, not statistical optimization.

---

**Keywords**: large language models, hallucination, knowledge graphs, RAG, SHACL validation, truth-constrained architectures

**Word count**: 148 words

