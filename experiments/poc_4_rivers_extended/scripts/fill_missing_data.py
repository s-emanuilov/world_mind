# Step 2: Fill missing data using LLM
import csv
import os
import requests
import json
from dotenv import load_dotenv
import re

load_dotenv()

def extract_other_names_from_abstract(abstract: str) -> str:
    """
    Extract alternative/variant names from the abstract deterministically using regex.
    Looks for sentences containing cues like 'Variant names', 'Other names', and 'also known as'.
    Returns a semicolon-separated string, or empty string if none found.
    """
    if not abstract:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", abstract)

    candidates: list[str] = []

    # 1) Sentences with explicit cues
    cue_patterns = [
        r"(Variant names? (are|include)[:\s]+[^\.!?]+)",
        r"(Other names?[:\s]+[^\.!?]+)",
        r"(Also known as[:\s]+[^\.!?]+)",
    ]

    for pat in cue_patterns:
        for match in re.finditer(pat, text, flags=re.IGNORECASE):
            span_text = match.group(1)
            # Prefer quoted names if present
            quoted = re.findall(r'"([^"\n]+)"', span_text)
            if quoted:
                candidates.extend([q.strip() for q in quoted])
            else:
                # Split by commas and 'and'
                # Remove leading cue phrase
                cleaned = re.sub(r"^(Variant names? (are|include)|Other names?|Also known as)[:\s]+", "", span_text, flags=re.IGNORECASE)
                parts = re.split(r",| and ", cleaned)
                for p in parts:
                    name = p.strip().strip(". ;:")
                    if name and len(name) < 200:
                        candidates.append(name)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    return ";".join(unique)


def get_llm_response(river_name, abstract, missing_fields):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")

    prompt = f"""
    Given the following information about the river '{river_name}', which is a river in the US:

    Abstract:
    {abstract}

    Please fill in the following missing fields based ONLY on the information available in the abstract.
    If a field cannot be filled from the abstract, leave it empty.
    Do not add any information that is not explicitly present in the abstract.

    Additionally, please extract any alternative names for the river mentioned in the abstract. Look for phrases like 'also known as', 'or', 'bore several other names', etc. Provide them in a field called 'otherNames', separated by a semicolon (;). If there are no alternative names, leave the field empty.

    Missing fields: {', '.join(missing_fields)}

    Provide the response as a JSON object with the field names as keys and the extracted information as values.
    For example:
    {{
      "fieldName1": "value1",
      "fieldName2": "",
      "otherNames": "Alternative Name 1;Alternative Name 2"
    }}
    """

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            data=json.dumps({
                "model": "google/gemini-2.5-flash-lite",
                "temperature": 0,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # The response may contain markdown code block syntax ```json ... ```
        if content.strip().startswith('```json'):
            content = content.strip()[7:-3].strip()
        
        return json.loads(content)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the API request: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {response.text}")
        return None


def process_csv(input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        if 'otherNames' not in header:
            header.append('otherNames')
        writer.writerow(header)

        for i, row in enumerate(reader):
            # To prevent accidental high costs, we will only process first 10 for now.
            # The user can remove this line to process the entire file.
            if i >= 10_000:
                # Stop after processing two rivers during testing
                break

            # Build a complete row_dict that includes every header key (including 'otherNames')
            row_dict = {h: '' for h in header}
            for idx, value in enumerate(row):
                if idx < len(header):
                    row_dict[header[idx]] = value
            
            abstract = row_dict.get('abstract')
            if not abstract:
                updated_row = [row_dict.get(field, '') for field in header]
                writer.writerow(updated_row)
                continue

            missing_fields = [field for field, value in row_dict.items() if not value]

            if not missing_fields and not row_dict.get('otherNames'):
                # Try deterministic extraction even if no LLM call is needed
                if not row_dict.get('otherNames'):
                    extracted = extract_other_names_from_abstract(abstract)
                    if extracted:
                        row_dict['otherNames'] = extracted
                updated_row = [row_dict.get(field, '') for field in header]
                writer.writerow(updated_row)
                continue
            
            river_name = row_dict.get('riverName')
            print(f"Processing {river_name}...")

            llm_data = get_llm_response(river_name, abstract, missing_fields)

            if llm_data:
                for field, value in llm_data.items():
                    if field in row_dict and (not row_dict.get(field) or field == 'otherNames'):
                         row_dict[field] = value

            # Fallback: if LLM did not provide otherNames, try deterministic extraction
            if not row_dict.get('otherNames'):
                extracted = extract_other_names_from_abstract(abstract)
                if extracted:
                    row_dict['otherNames'] = extracted
            
            updated_row = [row_dict.get(field, '') for field in header]
            writer.writerow(updated_row)
            print(f"Finished processing {river_name}. Saved to output.")


if __name__ == "__main__":
    input_csv_path = '../data/raw_rivers.csv'
    output_csv_path = '../data/raw_rivers_filled.csv'
    process_csv(input_csv_path, output_csv_path)
