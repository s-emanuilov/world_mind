# Gemma-3-4B-Rivers-Factual: LoRA Fine-Tuned for Factual Recall

This model is a LoRA fine-tuned variant of Google's Gemma 3-4B-Instruct, trained specifically for factual recall on the rivers question-answering dataset. The training employed 4-bit quantization with rank-16 LoRA adapters targeting attention and MLP layers (q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj) over 100 training steps at 2×10⁻⁴ learning rate. The training data consisted of 17,726 question-answer pairs where all responses were factual answers to questions about U.S. rivers. Surprisingly, this supervised fine-tuning resulted in significant performance degradation, achieving only 8.5% accuracy compared to the base model's 16.7% accuracy on the same evaluation set. This result provides empirical evidence that parameter optimization cannot reliably absorb factual knowledge across diverse question spaces, supporting the thesis that architectural enforcement rather than statistical learning is required for truth-constrained generation. The model serves as an important negative result demonstrating the limitations of fine-tuning approaches for factual grounding.

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

- **Dataset**: 17,726 question-answer pairs from rivers Q&A dataset
- **Format**: Multiple-choice questions with factual answers
- **Objective**: Maximize factual recall through supervised learning

## Performance

| Metric | Value |
|--------|-------|
| **Evaluation Accuracy** | 8.5% (1,499/17,725 correct) |
| **Base Model Accuracy** | 16.7% (comparison) |
| **Performance Change** | -8.2 percentage points (degradation) |

## Key Finding

This model demonstrates that supervised fine-tuning on factual data **fails to improve** and actually **degrades** performance compared to the base model. This negative result challenges the assumption that factual knowledge can be reliably encoded through parameter optimization and supports the need for architectural solutions (e.g., RAG, knowledge graphs) for factual grounding.

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
    "s-emanuilov/gemma-3-4b-rivers-factual"
)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-4b-it")

# Inference
question = "What is the approximate length of Aarons Creek in kilometers?"
options = ["44.64 km", "27.74 km", "44.00 km", "27.00 km", "45.00 km"]

prompt = f"{question}\nA) {options[0]}\nB) {options[1]}\nC) {options[2]}\nD) {options[3]}\nE) {options[4]}\n\nAnswer:"

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=10)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

## Research Implications

This model provides evidence that:
1. **Fine-tuning cannot encode diverse factual knowledge** across 17K examples
2. **Catastrophic forgetting** may occur even with instruction-tuned base models
3. **Parameter optimization alone is insufficient** for factual grounding
4. **Architectural solutions** (RAG, knowledge graphs) achieve 89% accuracy vs. 8.5%

## Citation

```bibtex
@model{emanuilov2025gemma_factual,
  author = {Emanuilov, Simeon},
  title = {Gemma-3-4B-Rivers-Factual: Evidence of Fine-Tuning Limitations},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/s-emanuilov/gemma-3-4b-rivers-factual}}
}
```

## License

This model inherits the Gemma license from Google. LoRA adapters are released under MIT License.





