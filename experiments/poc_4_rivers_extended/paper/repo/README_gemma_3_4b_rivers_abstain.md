# Gemma-3-4B-Rivers-Abstain: LoRA Fine-Tuned for Epistemic Calibration

This model is a LoRA fine-tuned variant of Google's Gemma 3-4B-Instruct, explicitly trained to abstain with "I don't know" responses when uncertain rather than generating potentially incorrect answers. The training employed 4-bit quantization with rank-16 LoRA adapters over 100 steps, using a mixed dataset where correct answers remained factual but incorrect answers were replaced with "I don't know" to teach epistemic discipline. Despite this explicit supervision signal targeting abstention behavior, the model achieved only 8.6% answer accuracy with 56.7% abstention precision—barely better than random guessing. This result demonstrates that parameter optimization cannot reliably encode genuine epistemic boundaries, as the model learned to produce "I don't know" as a behavioral pattern (63.7% recall) but without principled calibration. The findings provide strong empirical evidence that statistical learning approaches fail to achieve deterministic abstention and support the need for architectural enforcement through licensing oracles and formal validation mechanisms.

## Model Details

- **Base Model**: google/gemma-3-4b-it (instruction-tuned variant)
- **Training Method**: LoRA (Low-Rank Adaptation) with Unsloth AI
- **Quantization**: 4-bit for memory efficiency
- **LoRA Rank**: 16
- **Target Layers**: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- **Training Steps**: 100
- **Learning Rate**: 2×10⁻⁴
- **Optimizer**: AdamW with paged optimization

## Training Data

- **Dataset**: 17,726 question-answer pairs with mixed responses
- **Strategy**: Correct answers remain factual; incorrect answers replaced with "I don't know"
- **Objective**: Learn to abstain when uncertain rather than hallucinate

## Performance

| Metric | Value |
|--------|-------|
| **Answer Accuracy** | 8.6% (1,527/17,725) |
| **Abstention Precision** | 56.7% (appropriate abstentions / total abstentions) |
| **Abstention Recall** | 63.7% (appropriate abstentions / should abstain) |
| **Appropriate Abstentions** | 9,318 |
| **Inappropriate Abstentions** | 7,110 |

## Key Finding

This model demonstrates that **epistemic calibration cannot be learned statistically**. While the model successfully learned to produce "I don't know" as a token sequence (63.7% recall), it did so non-deterministically with near-random precision (56.7%). This shows that behavioral mimicry ≠ genuine epistemic self-awareness.

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-3-4b-it",
    load_in_4bit=True
)

# Load LoRA adapter
model = PeftModel.from_pretrained(
    base_model,
    "s-emanuilov/gemma-3-4b-rivers-abstain"
)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-4b-it")

# Inference
question = "What is the source elevation of an obscure river?"
prompt = f"{question}\n\nIf you are uncertain, respond with 'I don't know'.\n\nAnswer:"

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)  # May abstain, but unreliably
```

## Abstention Behavior Analysis

The model exhibits:
- **Learned pattern**: Successfully produces "I don't know" 63.7% of the time when appropriate
- **Poor precision**: Also abstains inappropriately 40% of the time (7,110 cases)
- **Non-deterministic**: Same question may get different responses (answer vs. abstain)
- **No epistemic grounding**: Cannot distinguish genuine uncertainty from surface patterns

## Comparison with Architectural Approach

| Approach | Abstention Precision | Determinism |
|----------|---------------------|-------------|
| **This Model (statistical)** | 56.7% | Non-deterministic |
| **Graph-RAG Oracle (architectural)** | >95% | Deterministic |

## Research Implications

This model provides critical evidence that:
1. **Behavioral mimicry ≠ epistemic self-awareness**
2. **Statistical learning cannot encode truth boundaries**
3. **Architectural enforcement is necessary** for reliable abstention
4. **Fine-tuning alone is insufficient** for truth-constrained generation

## Citation

```bibtex
@model{emanuilov2025gemma_abstain,
  author = {Emanuilov, Simeon},
  title = {Gemma-3-4B-Rivers-Abstain: Evidence that Epistemic Calibration Cannot Be Learned Statistically},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/s-emanuilov/gemma-3-4b-rivers-abstain}}
}
```

## License

This model inherits the Gemma license from Google. LoRA adapters are released under MIT License.

## Acknowledgments

Training conducted using Unsloth AI for efficient LoRA fine-tuning with 4-bit quantization on consumer hardware.


