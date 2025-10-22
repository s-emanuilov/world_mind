# Generate Questions and Answers Dataset from River Abstracts
# Step 3
import csv
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_qa_from_llm(river_name, abstract):
    """
    Generate 2 questions with 5 answers each (only one correct) based on the river abstract.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")

    prompt = f"""
    Given the following information about the river '{river_name}':

    Abstract:
    {abstract}

    Generate exactly 2 challenging questions about this river. Each question should have exactly 5 answer choices, with only ONE correct answer and 4 plausible but incorrect answers.

    Requirements:
    1. Questions must be self-contained and direct - do NOT mention "abstract", "provided information", or "based on the text"
    2. Keep questions concise and clear - avoid unnecessary words or phrases
    3. Focus on specific details, measurements, relationships, or technical aspects
    4. Make incorrect answers very plausible and similar to correct answers (same units, similar values)
    5. Ensure correct answers are explicitly stated in the abstract
    6. Questions should test deep understanding, not just fact recall

    Good examples:
    - "What is the elevation of the river's source?"
    - "Which counties does the river form a boundary between?"
    - "What is the river's length in kilometers?"
    - "Into which body of water does the river flow?"

    Bad examples:
    - "Based on the provided abstract, what is..."
    - "According to the information given..."
    - "The abstract describes..."

    Provide the response as a JSON object with this exact structure:
    {{
        "questions": [
            {{
                "question": "Direct question here?",
                "answers": [
                    "Correct answer",
                    "Incorrect answer 1", 
                    "Incorrect answer 2",
                    "Incorrect answer 3",
                    "Incorrect answer 4"
                ],
                "correct_answer_index": 0
            }},
            {{
                "question": "Second direct question here?",
                "answers": [
                    "Incorrect answer 1",
                    "Correct answer",
                    "Incorrect answer 2", 
                    "Incorrect answer 3",
                    "Incorrect answer 4"
                ],
                "correct_answer_index": 1
            }}
        ]
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
                "temperature": 0.3,  # Slightly higher for more varied incorrect answers
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
        elif content.strip().startswith('```'):
            content = content.strip()[3:-3].strip()
        
        return json.loads(content)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the API request: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {response.text}")
        return None


def process_csv(input_file, output_file, max_rivers=None):
    """
    Process the CSV file and generate Q&A dataset.
    """
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write header for Q&A dataset
        header = ['river_name', 'question_id', 'question', 'answer_1', 'answer_2', 'answer_3', 'answer_4', 'answer_5', 'correct_answer_index']
        writer.writerow(header)

        # Skip the original header
        next(reader)

        processed_count = 0
        for i, row in enumerate(reader):
            if max_rivers and processed_count >= max_rivers:
                break
                
            # Skip rows without abstract
            if len(row) < 3 or not row[2].strip():
                continue
                
            river_name = row[1]  # riverName column
            abstract = row[2]    # abstract column
            
            print(f"Processing {river_name}...")
            
            qa_data = get_qa_from_llm(river_name, abstract)
            
            if qa_data and 'questions' in qa_data:
                for q_idx, question_data in enumerate(qa_data['questions']):
                    question_id = f"{river_name}_{q_idx + 1}"
                    
                    # Write row for this question
                    row_data = [
                        river_name,
                        question_id,
                        question_data['question'],
                        question_data['answers'][0],
                        question_data['answers'][1], 
                        question_data['answers'][2],
                        question_data['answers'][3],
                        question_data['answers'][4],
                        question_data['correct_answer_index']
                    ]
                    writer.writerow(row_data)
                
                processed_count += 1
                print(f"Generated {len(qa_data['questions'])} questions for {river_name}")
            else:
                print(f"Failed to generate questions for {river_name}")
                
        print(f"Completed processing {processed_count} rivers")


if __name__ == "__main__":
    input_csv_path = '../data/raw_rivers_filled.csv'
    output_csv_path = '../data/river_qa_dataset.csv'
    
    # For testing, process only first 5 rivers. Remove max_rivers parameter to process all
    process_csv(input_csv_path, output_csv_path, max_rivers=10_000)
