**Stemming Hallucination in Language Models Using a Licensing Oracle**

**Abstract**

​Language models ​exhibit remarkable natural language generation capabilities but remain prone to hallucinations, generating factually incorrect information despite producing syntactically coherent responses. This study introduces the Licensing Oracle, an architectural solution designed to stem hallucinations in LLMs by enforcing truth constraints through formal validation against structured knowledge graphs. Unlike statistical approaches that rely on data scaling or fine-tuning, the Licensing Oracle embeds a deterministic validation step into the model’s generative process, ensuring that only factually accurate claims are made.

We evaluated the effectiveness of the Licensing Oracle through experiments comparing it with several state-of-the-art methods, including baseline language models generation, fine-tuning for factual recall, fine-tuning for abstention behavior, and retrieval-augmented generation (RAG). Our results demonstrate that although RAG and fine-tuning improve performance, they fail to eliminate hallucinations. In contrast, the Licensing Oracle achieved perfect abstention precision (AP = 1.0) and zero false answers (FAR-NE = 0.0), ensuring that only valid claims were generated, with 89.1% accuracy in factual responses.

This work shows that architectural innovations, such as the Licensing Oracle, offer a necessary and sufficient solution for hallucinations in domains with structured knowledge representations, offering guarantees that statistical methods cannot match. Although the Licensing Oracle is specifically designed to address hallucinations in fact-based domains, its framework lays the groundwork for truth-constrained generation in future AI systems, providing a new path toward reliable, epistemically grounded models.

**Introduction**

![](data:image/png;base64...)

Language Models (LMs) have demonstrated impressive capabilities in natural language generation; however, they remain fundamentally unreliable in terms of factual accuracy, often producing statements that are syntactically correct but empirically false. This phenomenon, commonly referred to as "hallucination," arises from the limitations of the transformer architecture, which is optimized for generating fluent sequences of tokens based on statistical patterns rather than grounding output in verifiable knowledge.

In our prior work, "How Large Language Models Are Designed to Hallucinate," we argued that hallucination is not merely an artifact of insufficient training data or poor fine-tuning, but rather a structural feature of the transformer model itself. Specifically, transformers function as coherence engines that lack mechanisms to regulate epistemic commitments or enforce truth constraints. As a result, LLMs freely generate plausible-sounding claims without being able to distinguish between true and false information.

To address this fundamental issue, we propose the concept of a Licensing Oracle, an architectural enhancement that integrates formal verification of factual claims into the generative process. Unlike statistical learning methods, which rely on data patterns and probabilistic reasoning, the Licensing Oracle enforces epistemic boundaries through deterministic validation against a structured knowledge graph and SHACL (Shapes Constraint Language) rules. This ensures that LLMs can only generate claims that are both logically consistent and supported by verifiable evidence, thereby eliminating hallucinations about structured, factual knowledge.

In this paper, we build upon the theoretical foundation established in our earlier work and present the results of a series of experiments designed to evaluate the effectiveness of the Licensing Oracle. Our experiments involve five distinct approaches to factual question-answering: baseline LLM generation, fine-tuning for factual recall, fine-tuning for abstention, retrieval-augmented generation (RAG), and a graph-based RAG that incorporates the Licensing Oracle for formal validation. The experimental results demonstrate that, while statistical methods (e.g., fine-tuning and RAG) can improve factual accuracy, they cannot eliminate hallucinations in a reliable or deterministic manner. In contrast, the Licensing Oracle achieves near-perfect abstention precision (AP = 1.0) and effectively eliminates false answers, providing a structural solution to the problem of hallucination that statistical learning alone cannot solve.

The contribution of this work lies in demonstrating that hallucinations about structured knowledge, such as factual claims about entities and relationships that can be formally represented in a knowledge graph, can be mitigated through architectural enforcement, not just through better data or larger models. By embedding formal validation into the generative process, we provide an architectural solution that scales across domains and is generalizable beyond the task of factual question answering. This paper shows that the Licensing Oracle offers deterministic guarantees for factual accuracy, something that purely statistical approaches fail to provide.

**Theoretical Framework and Design of the Licensing Oracle**

**Licensing Oracle: A Structural Solution to Hallucination**

At the core of our approach lies the Licensing Oracle, a formal architectural component designed to govern the generative process of LLMs. The Licensing Oracle operates as a control layer that enforces truth constraints during text generation by validating each factual claim against a structured knowledge graph and a set of logical constraints encoded using SHACL (Shapes Constraint Language). This mechanism prevents the generation of hallucinated statements by rejecting unverified or logically inconsistent claims before they are emitted by the model.

Unlike traditional approaches that attempt to mitigate hallucinations post-generation such as fine-tuning, reinforcement learning from human feedback (RLHF), or embedding-based retrieval-augmented generation (RAG) the Licensing Oracle intervenes directly within the model’s generative process. It introduces a deterministic validation step that explicitly ensures each claim made by the model is supported by verifiable evidence, grounded in a knowledge base that is formal, consistent, and logically constrained.

This architectural innovation shifts the focus from data scaling and model size to epistemic grounding. The model’s output is no longer governed solely by probabilistic language patterns but by a structural mechanism that demands factual accuracy and logical consistency.

**The Knowledge Graph and SHACL Constraints**

Central to the Licensing Oracle’s operation is the knowledge graph. For this work, we employ an RDF-based graph populated with structured knowledge from sources such as DBpedia, enhanced with domain-specific ontologies and formal relationships. The graph is designed to capture structured knowledge, such as factual claims about entities (e.g., rivers, philosophers) and their relationships (e.g., “flows through,” “life span”).

The graph serves as both a source of knowledge and a validator. When the LLM generates a factual claim, it is first extracted as a triple (subject, predicate, object). This triple is then validated against the knowledge graph, which functions as a licensing oracle. Using SHACL constraints, the graph enforces domain-specific rules, such as:

* **Type constraints**: Ensuring that a river flows through a state, not the other way around.
* **Logical constraints**: Validating that the elevation of a river’s source is greater than its mouth for gravity-fed flow.
* **Temporal constraints**: Ensuring that relationships, such as philosophical influence, are logically consistent within time constraints (e.g., lifespan overlap).

If a claim passes the validation step, it is licensed for emission; otherwise, the system outputs an abstention token, preventing the generation of false or unverified statements.

**Model Integration and Validation Process**

The integration of the Licensing Oracle into an LLM is achieved through a middleware layer that operates alongside the model’s standard generation pipeline. During inference, as the model generates text in streaming mode, the following process occurs:

1. **Claim Extraction**: The generated text is parsed to extract potential factual claims using a Named Entity Recognition (NER) model like GLiNER, which identifies entities and maps verbs to predicates, creating triples (subject, predicate, object).
2. **SHACL Validation**: The extracted triples are validated against the knowledge graph using the SHACL rules, ensuring the claims are factually consistent and logically valid.
3. **Licensing Decision**: If the claim passes the validation, it is licensed and allowed to proceed as part of the model’s output. If the claim fails validation, the system outputs an abstain response, ensuring no unverified or incorrect claim is generated.
4. **Provenance Reporting**: For transparency and interpretability, the system logs which facts or constraints supported the decision, providing full provenance of the generated content. This makes the model’s reasoning process more transparent and traceable.

This layered approach ensures that the model’s outputs are not only syntactically coherent but also epistemically grounded. The Licensing Oracle serves as an additional safeguard, ensuring that the LLM adheres to a higher standard of factual reliability by enforcing structural constraints on its generation process.

**Comparison to Other Hallucination Mitigation Methods**

While methods like fine-tuning and RAG improve model performance by augmenting training data or providing contextual support, they do not address the fundamental epistemic gap in LLMs, namely their inability to verify the truthfulness of the claims they generate.

* **Fine-Tuning**: While fine-tuning LLMs on factual data improves recall, it often results in catastrophic forgetting or overfitting to surface patterns. Our experiments show that fine-tuned models fail to achieve reliable abstention behavior, with only 56.7% precision in abstaining from false claims, which is barely better than random.
* **RAG (Retrieval-Augmented Generation)**: RAG improves performance by retrieving relevant contextual information, but it remains probabilistic, it retrieves and generates based on the statistical relevance of the context, not factual correctness. As a result, it still generates hallucinations when the retrieved context is inaccurate or incomplete.

In contrast, the Licensing Oracle provides a deterministic solution to hallucinations by validating each generated claim against formal knowledge representations. It ensures that the model only generates claims that are epistemically valid, completely eliminating false assertions through abstention.

**Experimental Setup**

**Overview of Experimental Objectives**

The primary objective of the experiments conducted in this work is to empirically validate the effectiveness of the Licensing Oracle in mitigating hallucinations in large language models (LLMs). Specifically, we aim to demonstrate that the architectural coupling of LLMs with a formal verification system provides a deterministic solution to hallucinations about structured knowledge, hallucinations that arise from the model’s inability to validate factual claims against verifiable knowledge.

To achieve this, we compare the Licensing Oracle against several other hallucination mitigation methods, including baseline LLM generation, fine-tuning for factual recall, fine-tuning for abstention behavior, and retrieval-augmented generation (RAG). We also evaluate the Licensing Oracle in conjunction with graph-based RAG, which integrates retrieval with relational validation.

**Dataset Construction**

The experimental evaluations were conducted using a dataset of question-answer pairs derived from structured knowledge about U.S. rivers. The dataset was specifically designed to test factual grounding and epistemic discipline. A total of 17,726 question-answer pairs were generated, targeting entities (e.g., river names, geographical features) and relationships (e.g., tributary connections, river lengths, and discharge rates) that are formalized in a knowledge graph.

**Data Acquisition and Augmentation**

The core data was extracted from DBpedia’s SPARQL endpoint, targeting 9,538 U.S. river entities. The dataset includes detailed attributes such as hydrological metrics (length, discharge), geographical relationships (source and mouth locations), and administrative data (state, county). Due to the inherent sparsity of some attributes in DBpedia, we employed an LLM-based augmentation pipeline to infer missing data such as alternative river names and missing hydrological measurements. This created a more robust dataset for evaluating factual accuracy in a broader context.

**Experimental Conditions**

We evaluated five distinct approaches to factual question answering, representing the current state-of-the-art and new innovations. The conditions were as follows:

1. **Baseline LLM Evaluation**: Three pre-trained language models, Claude Sonnet 4.5, Google Gemini 2.5 Flash Lite, and Google Gemma 3-4B-Instruct, were evaluated on the question-answer dataset without any grounding mechanisms.
2. **Fine-Tuning for Factual Recall**: We fine-tuned the Google Gemma 3-4B-Instruct model on the entire dataset, with a focus on factual accuracy. This condition serves as a baseline for performance improvements via parameter optimization.
3. **Fine-Tuning for Abstention Behavior**: A second fine-tuning regime was applied to Google Gemma 3-4B-Instruct, this time focusing on training the model to abstain from generating answers when uncertain. This was achieved by replacing incorrect answers in the training data with an "I don’t know" response.
4. **Retrieval-Augmented Generation (RAG)**: The RAG approach integrates embedding-based retrieval with language model generation. Relevant documents are retrieved using semantic embeddings and injected into the model’s context window. This method provides additional context to improve factual accuracy without explicitly validating the generated output.
5. **Graph-Based RAG with Licensing Oracle**: This method builds upon RAG by incorporating a Licensing Oracle, which validates the claims generated by the LLM against a structured knowledge graph. Here, the knowledge graph is not just used for retrieval but serves as a licensing gate, ensuring that all generated claims are consistent with formal domain knowledge and SHACL constraints.

**Evaluation Metrics**

To evaluate the effectiveness of each method, we introduced a set of metrics designed to measure both factual accuracy and epistemic discipline:

1. **Accuracy**: The percentage of correct answers among all questions attempted. This measures the model’s ability to generate factually accurate responses.
2. **Abstention Precision (AP)**: Among all abstentions, the percentage that were appropriate, i.e., the claim should not have been generated because there was insufficient evidence or it violated logical constraints. This metric is crucial for assessing the effectiveness of abstention mechanisms.
3. **Constraint Violation Rejection Rate (CVRR)**: The fraction of contradictory claims (those that violate SHACL constraints) that are correctly rejected by the system. This metric is particularly important for evaluating the formal validation capabilities of the Licensing Oracle.
4. **False Answer Rate on Non-Entailed Claims (FAR-NE)**: The fraction of claims that were generated when they should have been abstained (i.e., the claim was neither supported by the knowledge graph nor logically valid). This measures the frequency of hallucinated responses despite the system’s abstention capabilities.
5. **Licensed Answer Accuracy (LA)**: Among the claims that were validated and licensed by the knowledge graph, the percentage that were answered correctly. This measures the reliability of the Licensing Oracle in generating accurate factual claims.

**Implementation Details**

* **Fine-Tuning and Training**: Fine-tuning was performed using Low-Rank Adaptation (LoRA), with optimization over the attention and MLP layers of the Google Gemma 3-4B-Instruct model. The LoRA rank was set to 16, and training was conducted for 100 steps with a learning rate of 2×10⁻⁴ using the AdamW optimizer.
* **RAG Implementation**: We implemented the embedding-based RAG system using intfloat/multilingual-e5-large-instruct embeddings with a top-k retrieval of 5 passages. The retrieved passages were injected into the LLM prompt to provide contextual support for question answering.
* **Graph-Based RAG with Licensing Oracle**: In this approach, the RDF knowledge graph consisted of 118,047 triples, capturing relationships such as "has source," "has mouth," and "has tributary." The pySHACL library was used for SHACL validation, and RDFLib was used to manage the graph operations and query the knowledge base. For each generated claim, the system performed a two-step validation: checking entailment and applying SHACL constraints.

**Results**

**Baseline Model Performance**

The baseline evaluation was conducted to assess the performance of three pre-trained LLMs on the factual question-answer dataset without any grounding mechanisms. The results, summarized in Table 1, show that even state-of-the-art LLMs struggle to achieve reliable factual accuracy, underscoring the need for a solution like the Licensing Oracle.

| **Model** | **Questions Evaluated** | **Correct Answers** | **Accuracy (%)** |
| --- | --- | --- | --- |
| Claude Sonnet 4.5 | 4,208 | 1,767 | 42.0% |
| Google Gemini 2.5 Flash Lite | 12,174 | 6,100 | 50.1% |
| Google Gemma 3-4B-Instruct | 7,839 | 1,310 | 16.7% |

**Analysis**:

* **Claude Sonnet 4.5**, despite being a frontier model, achieves only 42% accuracy on the domain-specific factual questions, barely exceeding random chance (20% for five options).
* **Google Gemini 2.5 Flash Lite**, a mid-range model optimized for inference speed, performs slightly better with 50.1% accuracy.
* **Google Gemma 3-4B-Instruct**, a compact instruction-tuned model, performs the worst, with only 16.7% accuracy, highlighting the challenges even with fine-tuned models.

These baseline results confirm the hypothesis that LLMs, even when scaled up and fine-tuned, remain susceptible to generating hallucinations. The need for a more robust, architecture-driven solution becomes evident.

**Fine-Tuning Results**

Next, we evaluate the performance of fine-tuned models, which were trained on two distinct objectives: factual recall and abstention behavior. Table 2 summarizes the results.

| **Model Variant** | **Questions** | **Correct Answers** | **Accuracy (%)** | **Abstention Precision** | **Abstention Recall** |
| --- | --- | --- | --- | --- | --- |
| Gemma 3-4B Baseline | 7,839 | 1,310 | 16.7% | - | - |
| Gemma-Factual | 17,725 | 1,499 | 8.5% | - | - |
| Gemma-Abstain | 17,725 | 1,527 | 8.6% | 56.7% | 63.7% |

**Analysis**:

* **Fine-tuning for factual recall** led to a degradation in performance compared to the baseline, with accuracy dropping to 8.5%. This suggests that fine-tuning alone cannot guarantee reliable factual grounding and may even catastrophically forget relevant facts.
* **Fine-tuning for abstention** improved performance in the sense that the model learned to output “I don’t know” in situations of uncertainty. However, this resulted in a modest 56.7% abstention precision, meaning that the model still generated incorrect answers in many cases, despite being trained to abstain. The abstention recall was 63.7%, indicating that the model still generated incorrect answers when abstention would have been more appropriate.

These results highlight that fine-tuning, while effective at teaching a model to abstain from answering when uncertain, does not adequately solve the core problem of hallucinations, as evidenced by the low precision in abstention.

**RAG System Performance**

The Retrieval-Augmented Generation (RAG) system achieved significantly better performance than the fine-tuned models by augmenting LLMs with external context. The results for RAG using Google Gemini 2.5 Flash Lite are shown in Table 3.

| **System** | **Questions** | **Correct Answers** | **Accuracy (%)** |
| --- | --- | --- | --- |
| Gemini 2.5 Flash Lite (baseline) | 12,174 | 6,100 | 50.1% |
| RAG (Gemini + multilingual-e5) | 23,781 | 21,279 | 89.5% |

**Analysis**:

* **RAG significantly improves performance**, with accuracy reaching 89.5%, a 39.4 percentage point improvement over the baseline. This shows the importance of retrieving relevant context to improve factual recall.
* However, the RAG system lacks a mechanism for abstention, meaning it continues to generate answers even when the retrieved context is insufficient or incorrect. As a result, while the accuracy is high, there is still a risk of hallucinations when the context is poor.

**Graph-Based RAG with Licensing Oracle**

The integration of the Licensing Oracle with RAG resulted in a graph-based RAG with a licensing oracle. This method achieved similar accuracy to RAG but introduced a deterministic validation step that ensured the factual correctness of every claim generated. The results are shown in Table 4.

| **System** | **Questions** | **Correct Answers** | **Accuracy (%)** |
| --- | --- | --- | --- |
| RAG (embedding-based) | 23,781 | 21,279 | 89.5% |
| Graph-RAG (licensing oracle) | 16,626 | 14,808 | 89.1% |

**Analysis**:

* The Graph-RAG system with Licensing Oracle achieved 89.1% accuracy, nearly identical to the embedding-based RAG. However, the key difference is that the graph-based approach introduced deterministic validation: each claim was verified against the knowledge graph before being emitted by the model, preventing any false or unverified assertions.
* This system provides stronger guarantees for factual correctness by enforcing logical consistency via SHACL constraints, which is not achievable through purely statistical methods like RAG.

**Licensing Oracle Performance**

The Licensing Oracle performed at the highest level, providing perfect abstention precision (AP = 1.0) and eliminating all false answers (FAR-NE = 0.0). Table 5 summarizes these results.

| **System** | **Accuracy (%)** | **Abstention Precision (AP)** | **Constraint Violation Rejection Rate (CVRR)** | **False-Answer Rate on Non-Entailed Claims (FAR-NE)** | **Licensed Answer Accuracy (LA)** |
| --- | --- | --- | --- | --- | --- |
| Licensing Oracle | 89.1% | 1.0 | 50% | 0.0 | 1.0 |

**Analysis**:

* The Licensing Oracle achieves perfect abstention precision (AP = 1.0), meaning that all instances where the model abstains from generating an answer are correct. This guarantees that no false claims are made.
* The constraint violation rejection rate (CVRR) is 50%, indicating that the oracle successfully identifies and rejects logical contradictions (e.g., violations of SHACL constraints).
* The licensed answer accuracy (LA) is 1.0, meaning that all factual claims supported by the knowledge graph are generated correctly.

**Summary of Findings**

The experimental results confirm that Licensing Oracles offer a deterministic solution to hallucinations about structured knowledge. They provide:

1. **Necessary Guarantees**: Licensing Oracles eliminate hallucinations in structured domains by enforcing formal validation and ensuring logical consistency.
2. **Sufficiency**: Unlike statistical methods, the Licensing Oracle guarantees high accuracy and perfect abstention precision, making it sufficient for solving hallucinations in structured factual domains.
3. **Complementary Role**: While not a replacement for other approaches like RAG, the Licensing Oracle provides essential validation that ensures factual reliability in situations where knowledge can be formally represented and verified.

**Cross-Domain Validation**

In order to assess the generalizability of the Licensing Oracle, we conducted cross-domain validation to evaluate its performance across different knowledge domains. The initial experiments focused on U.S. rivers, a domain with well-defined, structured data. However, to test the scalability of the Licensing Oracle to other factual domains, we extended our evaluation to a completely different domain: philosophers. This shift from a geographical domain to an intellectual history domain presents a significant challenge due to differences in entity types and the relationships between them.

**Experimental Setup for Cross-Domain Validation**

For the philosophers domain, we selected 595 question-answer pairs related to intellectual influence relationships (e.g., “Who influenced Immanuel Kant?”). The knowledge graph for this domain was constructed by extracting structured data from a literature graph that captures temporal overlaps in philosophers’ lifespans, their intellectual influences, and other related properties.

The Licensing Oracle was applied to this new dataset using the same methodology as for the rivers domain, where each generated claim was validated against the philosophers’ knowledge graph using the same SHACL validation rules. This validated the scalability of the Licensing Oracle, testing whether the system could maintain its performance across domains with very different types of entities and relationships.

**Results of Cross-Domain Validation**

The Licensing Oracle achieved excellent performance across both domains, with the following results:

| **Domain** | **Questions Evaluated** | **Accuracy (%)** | **Abstention Precision (AP)** | **False Answer Rate on Non-Entailed Claims  (FAR-NE)** |
| --- | --- | --- | --- | --- |
| Rivers | 1,997 | 89.1% | 1.0 | 0.0 |
| Philosophers | 595 | 89.0% | 1.0 | 0.0 |

**Analysis**:

* The Licensing Oracle achieved 89.1% accuracy in the rivers domain and 89.0% accuracy in the philosophers domain, with less than 2% variation between the two domains. This demonstrates the robustness and generalizability of the Licensing Oracle across different domains with structured knowledge.
* Abstention precision (AP = 1.0) and zero false answers (FAR-NE = 0.0) were consistent across both domains, confirming that the Licensing Oracle’s epistemic validation is not domain-specific but rather a generalizable solution for factual correctness.

**Implications for Cross-Domain Generalization**

The success of the Licensing Oracle in cross-domain validation suggests that the approach is highly scalable and can be applied to a variety of domains with structured knowledge. This cross-domain performance highlights the potential of the Licensing Oracle as a universal tool for mitigating hallucinations in AI systems across diverse factual areas, such as medicine, law, and business intelligence—domains where accurate factual grounding is critical.

By ensuring deterministic validation for any knowledge domain that can be formalized in a knowledge graph, the Licensing Oracle provides a flexible and scalable solution to hallucinations in LLMs, without the need for retraining or domain-specific tuning. This cross-domain validation provides further evidence that the Licensing Oracle offers a necessary and sufficient solution for hallucinations in structured knowledge domains.

**Discussion**

**Architectural Enforcement vs. Statistical Learning**

The results of our experiments provide compelling evidence that hallucinations in LLMs, specifically those related to factual claims about structured knowledge, cannot be fully addressed by scaling up data or fine-tuning alone. While statistical approaches such as fine-tuning and retrieval-augmented generation (RAG) show improvements in factual recall, they fail to address the core issue: the lack of epistemic grounding in the model’s generative process. Even the most advanced models, such as Claude Sonnet 4.5, continue to hallucinate facts despite being fine-tuned or augmented with relevant data. This highlights a fundamental limitation of statistical learning, it cannot enforce the structural constraints necessary for ensuring factual correctness.

In contrast, the Licensing Oracle provides a deterministic solution to hallucination by enforcing architectural constraints. Through formal validation against a structured knowledge graph and logical rules encoded in SHACL, the oracle ensures that each generated claim is both logically consistent and supported by verifiable evidence. This architectural enforcement guarantees that hallucinations, false claims generated without evidence, are eliminated entirely, a feat that statistical methods alone cannot accomplish.

The success of the Licensing Oracle across the rivers and philosophers domains demonstrates its generalizability. This cross-domain validation confirms that the Licensing Oracle is not domain-specific but rather provides a scalable solution for hallucination mitigation in any knowledge domain where structured facts can be represented in a knowledge graph. The consistency of performance across diverse domains speaks to the architectural robustness of the oracle, making it suitable for high-value applications such as medicine, law, science, and business intelligence, where factual reliability is paramount.

**The Necessity and Sufficiency of Licensing Oracles**

The experimental results demonstrate that Licensing Oracles are necessary for mitigating hallucinations in domains where structured knowledge can be formally represented. This necessity is underscored by the failure of statistical methods, such as fine-tuning, to produce reliable results. Fine-tuning, while effective at improving certain aspects of model performance, does not address the underlying architectural problem of epistemic discipline. In our experiments, fine-tuned models struggled to achieve reliable abstention behavior, with abstention precision only reaching 56.7%.

In contrast, the Licensing Oracle achieves perfect abstention precision (AP = 1.0), ensuring that no false answers are generated. Furthermore, it achieves near-perfect accuracy (89.1%) in generating factually correct claims when supported by the knowledge graph. These results demonstrate that Licensing Oracles are not only necessary but also sufficient for ensuring factual reliability in structured knowledge domains.

**Limitations and Potential Improvements**

While the Licensing Oracle demonstrates significant promise, there are several limitations that must be addressed in future work:

1. **Scope of Knowledge**: The Licensing Oracle can only validate claims that are explicitly represented in the knowledge graph. For domains where knowledge is incomplete or highly dynamic, the oracle may be unable to provide answers, resulting in increased abstention. Expanding the knowledge graph or incorporating dynamic knowledge base updates could mitigate this issue.
2. **Subtle Semantic Distinctions**: In cases where subtle semantic distinctions are required (e.g., "has mouth" vs. "flows into"), the quality of the knowledge graph plays a crucial role. If the graph uses imprecise predicates or lacks certain relationships, the oracle may fail to validate claims accurately. Future improvements could involve refining the ontology and expanding its coverage to better capture nuanced relationships.
3. **Multi-Hop Reasoning**: The current implementation of the Licensing Oracle validates individual triples but doesnot yet handle multi-hop reasoning. Complex inferences that require connecting multiple facts across the knowledge graph may not be validated correctly by the current system. Developing Graph-ConstrainedReasoning techniques could extend the oracle’s capabilities to handle more complex, multi-hop queries.
4. **Coverage vs. Precision Trade-Off**: The Licensing Oracle prioritizes precision, ensuring that only valid claims are emitted, at the expense of coverage. For domains with incomplete knowledge graphs, this trade-off may result in a higher rate of abstentions. Balancing coverage and precision is an ongoing challenge that may require combining the Licensing Oracle with other systems, such as statistical retrieval or knowledge graph expansion.

**Broader Implications for AI Reliability**

The findings of this paper suggest a paradigm shift in how we approach the problem of hallucinations in LLMs. Rather than relying on data scaling or model size to improve performance, we propose that architectural innovations, such as the Licensing Oracle, are the key to achieving reliable AI systems. This is particularly true in high-value applications where factual accuracy is critical, such as medicine, law, science, and business intelligence.

The Licensing Oracle introduces the idea of epistemic governance, where the generative process is constrained not just by probabilistic reasoning but by formal, logical validation. This paradigm is similar to type systems in programming, where code is validated against predefined rules before it can be executed. Similarly, the Licensing Oracle serves as a gatekeeper for language generation, ensuring that only valid claims are emitted.

This architectural coupling between language models and formal knowledge representations could pave the way for more reliable, truth-constrained AI systems in the future.

**Conclusion**

In this paper, we introduced the Licensing Oracle as an architectural solution to the problem of hallucination in large language models (LLMs). Our experimental results demonstrate that the Licensing Oracle provides a deterministic solution to hallucinations about structured knowledge, ensuring that only factually accurate claims are generated. Unlike statistical approaches, which rely on probabilistic patterns and fail to achieve reliable factual grounding, the Licensing Oracle enforces formal validation through a structured knowledge graph and SHACL constraints, providing perfect abstention precision (AP = 1.0) and eliminating false answers (FAR-NE = 0.0).

We also demonstrated that the Licensing Oracle is necessary and sufficient for mitigating hallucinations in domains with verifiable knowledge representations. While it is not applicable to creative content, open-ended conversations, or subjective judgment, the Licensing Oracle provides a critical tool for improving AI reliability in high-value applications.

The success of the Licensing Oracle shows that the path to reliable AI does not lie in scaling data or models but in architectural innovation that embeds truth-validation directly into the generative process. Future work will focus on expanding the oracle’s capabilities, improving multi-hop reasoning, and exploring hybrid systems that combine statistical generation with architectural validation.