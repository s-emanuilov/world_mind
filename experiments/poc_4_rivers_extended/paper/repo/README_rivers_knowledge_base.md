# Rivers Knowledge Base Dataset

This dataset contains comprehensive structured knowledge about 9,538 U.S. river entities extracted from DBpedia's SPARQL endpoint. Each river is described through 21 attributes including hydrological metrics (length, discharge, watershed area), geographic coordinates (source and mouth locations with elevations), tributary relationships, administrative jurisdictions (state, county, country), and river system memberships. The dataset is provided in two versions: the raw extraction (`raw_rivers.csv`, 5.3MB) containing the original DBpedia data, and an enhanced version (`raw_rivers_filled.csv`, 6.2MB) augmented with LLM-extracted values for missing attributes and an additional `otherNames` field capturing toponymic variants. This knowledge base serves as the foundation for the experimental validation of truth-constrained LLM architectures, providing ground truth for question generation, knowledge graph construction, and hallucination detection evaluation. The structured nature of the data—with explicit modeling of numerical measurements, spatial hierarchies, and relational constraints—makes it ideal for testing formal validation mechanisms and ontological grounding approaches.

## Files

- `raw_rivers.csv` (5.3MB) - Original DBpedia extraction with 9,538 river entities
- `raw_rivers_filled.csv` (6.2MB) - Enhanced version with LLM-augmented missing values and alternative names

## Attributes (21 total)

- **Hydrological**: length (m), discharge (m³/s), watershed area (km²)
- **Geographic**: source location, source mountain, source state, source elevation (m), mouth location, mouth state, mouth elevation (m)
- **Relationships**: river system, left tributary, right tributary
- **Administrative**: state, county, country
- **Identifiers**: river URI, river name, abstract, wikiPageID, other names

## Usage

```python
import pandas as pd

# Load raw dataset
df_raw = pd.read_csv('raw_rivers.csv')

# Load enhanced dataset
df_enhanced = pd.read_csv('raw_rivers_filled.csv')

# Example: Rivers in California
ca_rivers = df_enhanced[df_enhanced['state'].str.contains('California', na=False)]
print(f"Found {len(ca_rivers)} rivers in California")
```

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{emanuilov2025rivers_kb,
  author = {Emanuilov, Simeon},
  title = {Rivers Knowledge Base: Structured River Data from DBpedia},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/datasets/s-emanuilov/rivers-knowledge-base}}
}
```

## License

This dataset is derived from DBpedia, which is licensed under CC BY-SA 3.0. The enhanced version with LLM-augmented values is released under the same license.

## Source

Original data extracted from DBpedia SPARQL endpoint (https://dbpedia.org/sparql) using queries targeting U.S. river entities with comprehensive attribute retrieval.


