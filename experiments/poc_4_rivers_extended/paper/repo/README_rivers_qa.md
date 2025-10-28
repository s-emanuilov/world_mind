# Rivers Q&A Evaluation Dataset

This dataset contains 17,726 multiple-choice questions systematically generated from the rivers knowledge base for evaluating factual grounding and hallucination detection in large language models. Each question follows a five-option multiple-choice format where one option is verifiably correct based on the source river abstract, and four options serve as plausible distractors with similar value ranges or related geographic entities. The dataset is provided in two variants: canonical ordering (`river_qa_dataset.csv`) and randomized answer positions (`river_qa_dataset_shuffled.csv`) to eliminate positional bias during model evaluation. Questions probe specific numerical values (lengths, elevations, discharge rates), geographic relationships (tributaries, mouth locations, jurisdictions), and categorical properties (river systems, administrative boundaries), ensuring comprehensive coverage of factual knowledge types. This evaluation dataset enables rigorous benchmarking of LLM factual accuracy in structured domains and supports research on truth-constrained architectures and knowledge-grounded generation.

## Files

- `river_qa_dataset.csv` (3.6MB) - Questions with canonical answer ordering
- `river_qa_dataset_shuffled.csv` (3.6MB) - Questions with randomized answer positions

## Dataset Statistics

- **Total questions**: 17,726
- **Rivers covered**: 8,863 unique river entities
- **Questions per river**: Typically 2
- **Answer format**: 5-option multiple choice (A-E)
- **Question types**: Numerical measurements, geographic relationships, categorical memberships

## Format

Each row contains:
- `river_name`: Entity name
- `question_id`: Unique identifier
- `question`: Question text
- `answer_1` through `answer_5`: Answer options
- `correct_answer_index`: Index of correct answer (0-4)

## Example

```csv
river_name,question_id,question,answer_1,answer_2,answer_3,answer_4,answer_5,correct_answer_index
Aarons Creek (Dan River tributary),Aarons Creek_1,What is the approximate length of Aarons Creek in kilometers?,44.64 km,27.74 km,44.00 km,27.00 km,45.00 km,0
```

## Usage

```python
import pandas as pd

# Load shuffled version (recommended for evaluation)
df = pd.read_csv('river_qa_dataset_shuffled.csv')

# Evaluate a model
def evaluate_model(model, df):
    correct = 0
    for idx, row in df.iterrows():
        question = row['question']
        options = [row[f'answer_{i+1}'] for i in range(5)]
        correct_idx = row['correct_answer_index']
        
        # Get model prediction (A-E)
        prediction = model.predict(question, options)
        if prediction == ['A', 'B', 'C', 'D', 'E'][correct_idx]:
            correct += 1
    
    return correct / len(df)
```

## Quality Controls

Questions were generated with strict quality requirements:
- Self-contained without meta-references to source material
- Plausible distractors prevent trivial elimination
- No linguistic cues telegraphing correct answers
- Verification against source abstracts for factual accuracy

## Citation

```bibtex
@dataset{emanuilov2025rivers_qa,
  author = {Emanuilov, Simeon},
  title = {Rivers Q\&A Dataset: Multiple-Choice Questions for LLM Factual Evaluation},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/datasets/s-emanuilov/rivers-qa}}
}
```

## License

CC BY-SA 4.0 - Questions derived from DBpedia content under CC BY-SA 3.0.


